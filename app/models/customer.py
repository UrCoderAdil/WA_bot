import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from app.db.database import Base
from app.core.utils import utcnow


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    preferred_language = Column(String(20), default="en")  # en, ur, roman_urdu
    total_orders = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    tags = Column(JSON, default=list)  # ["vip", "repeat_customer", "new"]
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, nullable=True)  # Which business this customer belongs to
    first_interaction = Column(DateTime, default=utcnow)
    last_interaction = Column(DateTime, default=utcnow, onupdate=utcnow)

    def __repr__(self):
        return f"<Customer {self.phone_number} ({self.name})>"
