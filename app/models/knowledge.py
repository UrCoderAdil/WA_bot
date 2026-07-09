import uuid
from sqlalchemy import Column, String, Text, DateTime
from app.db.database import Base
from app.core.utils import utcnow


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # The actual knowledge text
    category = Column(String(100), nullable=True)  # menu, policy, faq, product
    created_at = Column(DateTime, default=utcnow)

    def __repr__(self):
        return f"<KnowledgeEntry {self.title}>"
