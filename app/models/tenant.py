import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    business_type = Column(String(50), nullable=False)  # restaurant, clinic, fashion
    phone_number_id = Column(String(50), unique=True, nullable=False)  # WhatsApp Phone Number ID
    system_prompt = Column(Text, nullable=True)  # Custom AI personality per tenant
    tools_enabled = Column(JSON, default=list)  # List of tool names enabled
    api_keys = Column(JSON, default=dict)  # Tenant-specific API keys
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Tenant {self.name} ({self.business_type})>"
