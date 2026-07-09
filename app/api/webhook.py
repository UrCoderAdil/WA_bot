from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from app.core.config import settings
from app.services.ai import ai_assistant
from app.services.whatsapp import whatsapp_service

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    WhatsApp Cloud API Webhook Verification Endpoint.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        print("Webhook verified successfully!")
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

from app.services.business_logic import human_mode_sessions
from app.services.analytics import analytics_service
from app.services.crm import crm_service
from app.services.tenant_manager import tenant_manager
import time

async def process_whatsapp_message(phone_number: str, text: str, media_url: str = None,
                                   is_audio: bool = False, phone_number_id: str = None):
    """Background task to process AI and send response."""
    print(f"Processing message from {phone_number}: {text}")
    start_time = time.time()

    # 1. Check if session is in human mode
    if phone_number in human_mode_sessions:
        print(f"[{phone_number}] is in HUMAN MODE. AI is ignoring the message.")
        return

    # 2. Resolve the tenant (business) that owns the WhatsApp number this arrived on.
    tenant = await tenant_manager.get_tenant_by_phone_id(phone_number_id) if phone_number_id else None
    tenant_id = tenant["id"] if tenant else None
    system_prompt = tenant["system_prompt"] if tenant else None

    # 3. Update CRM — create/touch customer profile (scoped to the tenant)
    await crm_service.get_or_create_customer(phone_number, tenant_id=tenant_id)

    # 4. Generate AI Response (passing media_url + tenant persona if present)
    trace: dict = {}
    ai_response = await ai_assistant.generate_response(
        text, phone_number, media_url, trace=trace, system_prompt=system_prompt
    )

    response_time_ms = (time.time() - start_time) * 1000

    # 5. Log analytics event
    message_type = "audio" if is_audio else ("image" if media_url else "text")
    tools_used = trace.get("tools", [])
    await analytics_service.log_event(
        phone_number=phone_number,
        message_type=message_type,
        user_message=text,
        ai_response=str(ai_response),
        tool_called=", ".join(tools_used) if tools_used else None,
        response_time_ms=response_time_ms,
        escalated=phone_number in human_mode_sessions,
        tenant_id=tenant_id,
    )
    
    # 6. Send via WhatsApp (Text or Audio)
    if is_audio:
        from app.services.tts import generate_speech
        audio_path = await generate_speech(ai_response)
        await whatsapp_service.send_audio_message(phone_number, audio_path)
    else:
        await whatsapp_service.send_text_message(phone_number, ai_response)


@router.post("/webhook")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming WhatsApp messages.
    """
    try:
        body = await request.json()
        print("Received payload:", body)
        
        # Check if this is a WhatsApp status update or a message
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # The Phone Number ID identifies which business (tenant) received the message.
                    phone_number_id = value.get("metadata", {}).get("phone_number_id")

                    if "messages" in value:
                        for message in value["messages"]:
                            phone_number = message.get("from")

                            # Handle text messages
                            if "text" in message:
                                text = message["text"]["body"]
                                background_tasks.add_task(
                                    process_whatsapp_message, phone_number, text, None, False, phone_number_id
                                )

                            # Handle image messages (media ID resolved to a downloadable URL later)
                            elif "image" in message:
                                image = message["image"]
                                caption = image.get("caption", "")
                                background_tasks.add_task(
                                    process_whatsapp_message, phone_number, caption, image["id"], False, phone_number_id
                                )

                            # Handle audio messages (voice notes) — Gemini understands the audio natively.
                            elif "audio" in message:
                                audio_id = message["audio"]["id"]
                                background_tasks.add_task(
                                    process_whatsapp_message, phone_number, "", audio_id, True, phone_number_id
                                )
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error"}
