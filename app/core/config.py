from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "AI WhatsApp Business Assistant"
    DEBUG: bool = True
    
    # WhatsApp Config
    WHATSAPP_VERIFY_TOKEN: str = "your_verify_token_here"
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    
    # AI Config
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # DB Config
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # SLA & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    SLA_TARGET_MS: int = 3000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
