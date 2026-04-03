import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())