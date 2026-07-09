import hashlib
import hmac
import json
from collections import OrderedDict
from fastapi import APIRouter, Request, HTTPException, Query, BackgroundTasks
from app.core.config import settings
from app.services.ai import ai_assistant
from app.services.whatsapp import whatsapp_service

router = APIRouter()

# Bounded set of recently-seen WhatsApp message IDs. WhatsApp retries webhook delivery
# until it gets a 200, so without dedup the same message would be answered multiple times.
_seen_message_ids: "OrderedDict[str, None]" = OrderedDict()
_SEEN_MAX = 2000


def _already_processed(message_id: str) -> bool:
    """Return True if this message ID was seen before; otherwise record it (LRU-bounded)."""
    if not message_id:
        return False
    if message_id in _seen_message_ids:
        return True
    _seen_message_ids[message_id] = None
    if len(_seen_message_ids) > _SEEN_MAX:
        _seen_message_ids.popitem(last=False)  # evict oldest
    return False


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validate Meta's X-Hub-Signature-256 header. Skipped when no app secret is configured."""
    if not settings.WHATSAPP_APP_SECRET:
        return True  # local dev / secret not set
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header.split("=", 1)[1])

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

from app.services.handoff import handoff_manager
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
    if handoff_manager.is_active(phone_number):
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
        escalated=handoff_manager.is_active(phone_number),
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
        # Read the raw body once so we can both verify the signature and parse it.
        raw_body = await request.body()
        if not _verify_signature(raw_body, request.headers.get("X-Hub-Signature-256")):
            raise HTTPException(status_code=403, detail="Invalid signature")

        body = json.loads(raw_body)
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

                            # Skip messages we've already handled (WhatsApp retries on non-200).
                            if _already_processed(message.get("id")):
                                print(f"Duplicate message {message.get('id')} ignored.")
                                continue

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
    except HTTPException:
        raise  # let auth failures (e.g. bad signature) return their real status code
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error"}
