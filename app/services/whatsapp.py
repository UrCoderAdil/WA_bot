import httpx
from app.core.config import settings

class WhatsAppService:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to_phone_number: str, message: str):
        """
        Send a text message via WhatsApp Cloud API.
        """
        # If we are in local mocking mode and missing keys, just print
        if not settings.WHATSAPP_ACCESS_TOKEN or settings.WHATSAPP_ACCESS_TOKEN == "your_access_token_here":
            print(f"[MOCK WHATSAPP] Message to {to_phone_number}: {message}")
            return {"status": "mocked", "message": message}
            
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "text",
            "text": {"body": message}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Failed to send message: {e.response.text}")
                return None

    async def send_audio_message(self, to_phone_number: str, audio_url_or_id: str):
        """
        Send an audio message (.ogg) via WhatsApp Cloud API.
        """
        if not settings.WHATSAPP_ACCESS_TOKEN or settings.WHATSAPP_ACCESS_TOKEN == "your_access_token_here":
            print(f"[MOCK WHATSAPP] Audio Message to {to_phone_number}: [Audio File Generated: {audio_url_or_id}]")
            return {"status": "mocked", "audio": audio_url_or_id}
            
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "audio",
            "audio": {"link": audio_url_or_id}  # In production, this can also be an 'id'
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Failed to send audio message: {e.response.text}")
                return None

whatsapp_service = WhatsAppService()
