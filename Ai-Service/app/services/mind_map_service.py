from app.db import SessionLocal
from app.repositories.document_repository import get_document_by_id

def generate_mind_map(user_id: str, doc_id: str) -> str:
    db = SessionLocal()
    try:
        document = get_document_by_id(db, doc_id)
        if not document or document.user_id != user_id:
            return "@startmindmap\n* No document found or access denied.\n@endmindmap"
        
        if document.extraction_status == "COMPLETED" and document.mind_map_plantuml:
            return document.mind_map_plantuml
        elif document.extraction_status == "PENDING":
            return "@startmindmap\n* Document is still processing...\n@endmindmap"
        else:
            return "@startmindmap\n* Extraction failed or not started.\n@endmindmap"
    finally:
        db.close()
