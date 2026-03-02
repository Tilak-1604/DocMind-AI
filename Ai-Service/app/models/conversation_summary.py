import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.db import Base


class ConversationSummary(Base):
    """
    Stores a Gemini-generated rolling summary of older conversation turns
    for token-efficient memory management.

    When a conversation exceeds 6 turns, older messages are summarized by Gemini
    and stored here. The RAG engine injects this summary + last 4 recent turns
    into every prompt — preventing token explosion at scale.
    """
    __tablename__ = "conversation_summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), nullable=False, index=True, unique=True)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
