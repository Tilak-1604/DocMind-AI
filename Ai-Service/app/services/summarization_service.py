from app.db import SessionLocal
from app.repositories.document_repository import get_document_by_id

def summarize_document(user_id: str, doc_id: str) -> str:
    db = SessionLocal()
    try:
        document = get_document_by_id(db, doc_id)
        if not document or document.user_id != user_id:
            return "No document found or access denied."
        
        if document.extraction_status == "COMPLETED" and document.global_summary:
            return document.global_summary
        elif document.extraction_status == "PENDING":
            return "Document is still being processed. Please check back in a moment."
        else:
            return "Extraction failed or not started for this document."
    finally:
        db.close()
