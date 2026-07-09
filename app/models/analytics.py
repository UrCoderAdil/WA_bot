import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from app.db.database import Base
from app.core.utils import utcnow


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    phone_number = Column(String(20), nullable=False, index=True)
    message_type = Column(String(20), default="text")  # text, image, voice
    user_message = Column(String(1000), nullable=True)
    ai_response = Column(String(2000), nullable=True)
    tool_called = Column(String(100), nullable=True)  # e.g., "check_order_status"
    response_time_ms = Column(Float, nullable=True)
    escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow, index=True)

    def __repr__(self):
        return f"<AnalyticsEvent {self.message_type} from {self.phone_number}>"
