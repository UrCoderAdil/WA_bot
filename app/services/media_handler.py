import httpx
import base64
import mimetypes
from app.core.config import settings

GRAPH_API_VERSION = "v19.0"

# Some hosts (e.g. Wikimedia) reject requests without a User-Agent.
_DOWNLOAD_HEADERS = {"User-Agent": "WA-Bot/1.0 (+https://example.com)"}


async def _resolve_media_id_to_url(media_id: str, client: httpx.AsyncClient) -> str | None:
    """Resolve a WhatsApp media ID to a short-lived downloadable URL via the Graph API."""
    meta = await client.get(
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/{media_id}",
        headers={"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"},
    )
    meta.raise_for_status()
    return meta.json().get("url")


async def fetch_media_as_base64(media_ref: str) -> dict:
    """
    Download media and return a base64 dict suitable for Langchain's HumanMessage.

    `media_ref` may be either a public URL (used for local testing) or a WhatsApp
    Cloud API media ID. Media IDs are first resolved to a temporary download URL,
    and both the resolve and download calls are authenticated with the WhatsApp token.
    """
    try:
        is_url = media_ref.startswith("http://") or media_ref.startswith("https://")
        # Graph-hosted media requires the bearer token on the download request too.
        auth_headers = (
            {"Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"}
            if settings.WHATSAPP_ACCESS_TOKEN
            else {}
        )

        async with httpx.AsyncClient(follow_redirects=True) as client:
            if is_url:
                download_url, headers = media_ref, dict(_DOWNLOAD_HEADERS)
            else:
                download_url = await _resolve_media_id_to_url(media_ref, client)
                if not download_url:
                    print(f"Could not resolve media id {media_ref}")
                    return None
                headers = {**_DOWNLOAD_HEADERS, **auth_headers}

            response = await client.get(download_url, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if not content_type:
                content_type, _ = mimetypes.guess_type(media_ref)

            base64_data = base64.b64encode(response.content).decode("utf-8")
            return {"mime_type": content_type, "data": base64_data}
    except Exception as e:
        print(f"Error fetching media: {e}")
        return None
