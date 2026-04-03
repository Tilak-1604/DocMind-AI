import random
from app.db import SessionLocal
from app.models.extracted_data import ExtractedChunk

def generate_flashcards(user_id: str, doc_id: str, num_cards: int = 10):
    db = SessionLocal()
    try:
        chunks = db.query(ExtractedChunk).filter(
            ExtractedChunk.doc_id == doc_id,
            ExtractedChunk.user_id == user_id
        ).all()
        
        if not chunks:
            return {"error": "No data found. Document may still be processing or failed."}
            
        all_concepts = []
        for chunk in chunks:
            if chunk.key_concepts:
                 for concept in chunk.key_concepts:
                     all_concepts.append({
                         "question": f"What is meant by {concept.get('term', 'this term')}?",
                         "answer": concept.get("definition", "")
                     })
                     
        if not all_concepts:
             return {"error": "No concepts extracted from this document."}
             
        random.shuffle(all_concepts)
        return all_concepts[:num_cards]
    finally:
        db.close()