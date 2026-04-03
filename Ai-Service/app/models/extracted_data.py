from sqlalchemy import Column, String, Integer, JSON, ForeignKey, Text
from app.db import Base

class ExtractedChunk(Base):
    __tablename__ = "extracted_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    doc_id = Column(String(255), ForeignKey("documents.doc_id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    
    chunk_summary = Column(Text, nullable=True)
    key_concepts = Column(JSON, default=list)
    hierarchical_topics = Column(JSON, default=list)
    important_facts = Column(JSON, default=list)
