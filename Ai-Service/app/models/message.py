import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from app.db import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), index=True)  # Index for fast lookups
    role = Column(String(20), nullable=False)
    content = Column(LONGTEXT, nullable=False)   # LONGTEXT = up to 4GB, handles large LLM answers
    created_at = Column(DateTime, server_default=func.now(), index=True)  # Index for time-based queries
    
    # Composite index for common query pattern: fetch messages by conversation, ordered by time
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )