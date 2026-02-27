from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
