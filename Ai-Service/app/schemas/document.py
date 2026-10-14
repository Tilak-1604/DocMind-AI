from pydantic import BaseModel
from typing import Optional


class UploadResponse(BaseModel):
    status: str
    doc_id: str
    chunks_stored: int


class DocumentStatusResponse(BaseModel):
    doc_id: str
    extraction_status: str
    name: Optional[str] = None
