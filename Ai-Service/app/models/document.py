from sqlalchemy import Column, String, Integer, DateTime, Text, BigInteger
from sqlalchemy.sql import func
from app.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    doc_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    chunk_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), name="upload_date")
    
    # AI Service Metadata
    extraction_status = Column(String(50), default="PENDING")
    global_summary = Column(Text, nullable=True)
    mind_map_plantuml = Column(Text, nullable=True)