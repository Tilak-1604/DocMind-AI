from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Added for Single-Pass Extraction architecture
    extraction_status = Column(String(50), default="PENDING") # PENDING, COMPLETED, FAILED
    global_summary = Column(Text, nullable=True)
    mind_map_plantuml = Column(Text, nullable=True)