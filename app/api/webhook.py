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

async def process_whatsapp_message(phone_number: str, text: str):
    """Background task to process AI and send response."""
    print(f"Processing message from {phone_number}: {text}")
    
    # 1. Generate AI Response
    ai_response = await ai_assistant.generate_response(text, phone_number)
    
    # 2. Send via WhatsApp
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
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            phone_number = message.get("from")
                            text = message.get("text", {}).get("body")
                            
                            if text and phone_number:
                                # Send to background task so webhook can return 200 OK immediately
                                background_tasks.add_task(process_whatsapp_message, phone_number, text)
                            
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error"}
