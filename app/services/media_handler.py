import httpx
import base64
import mimetypes

async def fetch_media_as_base64(media_url: str) -> dict:
    """
    Downloads media from a URL and converts it to a base64 dictionary 
    suitable for Langchain's HumanMessage.
    If the URL is a local mock or Meta Media ID (in a real app), this 
    is where the Meta API download logic would go.
    """
    try:
        # For testing, we assume media_url is a public URL to an image or audio
        async with httpx.AsyncClient() as client:
            response = await client.get(media_url)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if not content_type:
                content_type, _ = mimetypes.guess_type(media_url)
            
            base64_data = base64.b64encode(response.content).decode("utf-8")
            
            return {
                "mime_type": content_type,
                "data": base64_data
            }
    except Exception as e:
        print(f"Error fetching media: {e}")
        return None
