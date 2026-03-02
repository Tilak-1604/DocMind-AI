import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    role = Column(String(20), nullable=False)
    content = Column(LONGTEXT, nullable=False)   # LONGTEXT = up to 4GB, handles large LLM answers
    created_at = Column(DateTime, server_default=func.now())