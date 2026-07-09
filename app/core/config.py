from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AI WhatsApp Business Assistant"
    DEBUG: bool = True
    
    # WhatsApp Config
    WHATSAPP_VERIFY_TOKEN: str = "your_verify_token_here"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    # App Secret (from Meta App dashboard). When set, incoming webhooks are verified
    # via the X-Hub-Signature-256 header. Leave empty to skip verification in local dev.
    WHATSAPP_APP_SECRET: str = ""
    
    # AI Config
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    # Model is configurable via .env. gemini-2.5-flash has a far more generous free-tier
    # quota than gemini-3.5-flash (which is capped at ~20 requests/day on the free tier).
    GEMINI_MODEL: str = "gemini-2.5-flash"
    # Embedding model for the knowledge base (RAG). embedding-001 is retired.
    GEMINI_EMBED_MODEL: str = "models/gemini-embedding-001"
    
    # DB Config
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # Frontend Deployment
    FRONTEND_URL: str = "https://frontend-zeta-rust-52.vercel.app"

    # SLA & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    SLA_TARGET_MS: int = 3000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
