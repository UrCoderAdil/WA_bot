from fastapi import FastAPI
from app.api import webhook
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="WhatsApp Business API Webhook Server",
    version="1.0.0",
)

# Include Routers
app.include_router(webhook.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "WhatsApp AI Assistant API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
