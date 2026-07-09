import os
import httpx
from app.core.config import settings

GRAPH_API_VERSION = "v19.0"


class WhatsAppService:
    def __init__(self):
        base = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
        self.api_url = f"{base}/messages"
        self.media_url = f"{base}/media"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def _is_mock(self) -> bool:
        """True when credentials are missing — used to keep local dev working without Meta."""
        return not settings.WHATSAPP_ACCESS_TOKEN or settings.WHATSAPP_ACCESS_TOKEN == "your_access_token_here"

    async def upload_media(self, file_path: str, mime_type: str = "audio/ogg") -> str | None:
        """
        Upload a local media file to WhatsApp and return its media ID.
        Required because WhatsApp cannot fetch local file paths — outgoing media
        must be referenced by an uploaded media ID (or a public URL).
        """
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, mime_type)}
                data = {"messaging_product": "whatsapp", "type": mime_type}
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.media_url,
                        headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
                        data=data,
                        files=files,
                    )
                    response.raise_for_status()
                    return response.json().get("id")
        except Exception as e:
            print(f"Failed to upload media: {e}")
            return None

    async def send_text_message(self, to_phone_number: str, message: str):
        """
        Send a text message via WhatsApp Cloud API.
        """
        # If we are in local mocking mode and missing keys, just print
        if self._is_mock():
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

    async def send_audio_message(self, to_phone_number: str, audio_path_url_or_id: str):
        """
        Send an audio message (.ogg) via WhatsApp Cloud API.

        `audio_path_url_or_id` may be a local file path (uploaded first to obtain a
        media ID), a public URL, or an already-uploaded media ID.
        """
        if self._is_mock():
            print(f"[MOCK WHATSAPP] Audio Message to {to_phone_number}: [Audio File Generated: {audio_path_url_or_id}]")
            return {"status": "mocked", "audio": audio_path_url_or_id}

        # Decide how WhatsApp should reference the audio.
        if audio_path_url_or_id.startswith(("http://", "https://")):
            audio_ref = {"link": audio_path_url_or_id}
        elif os.path.exists(audio_path_url_or_id):
            media_id = await self.upload_media(audio_path_url_or_id, mime_type="audio/ogg")
            if not media_id:
                return None
            audio_ref = {"id": media_id}
        else:
            # Assume it's already an uploaded media ID.
            audio_ref = {"id": audio_path_url_or_id}

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "audio",
            "audio": audio_ref,
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
