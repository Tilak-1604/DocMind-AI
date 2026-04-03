import json
from app.db import SessionLocal
from app.models.extracted_data import ExtractedChunk

def extract_key_topics(user_id: str, doc_id: str):
    db = SessionLocal()
    try:
        chunks = db.query(ExtractedChunk).filter(
            ExtractedChunk.doc_id == doc_id,
            ExtractedChunk.user_id == user_id
        ).all()
        
        if not chunks:
            return json.dumps({"error": "No data found. Document may still be processing or failed."})
            
        all_topics = []
        for chunk in chunks:
            if chunk.key_concepts:
                for concept in chunk.key_concepts:
                    all_topics.append({
                        "title": concept.get("term", ""),
                        "definition": concept.get("definition", "")
                    })
                    
        return json.dumps({"topics": all_topics})
    finally:
        db.close()
