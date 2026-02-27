from typing import List
from pinecone import Pinecone
from app.core.config import settings
from app.db import SessionLocal
from app.repositories.document_repository import get_document_with_owner

# Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)


def get_document_chunks(user_id: str, doc_id: str) -> List[str]:
    """
    Fetch all document chunks deterministically using Pinecone index.fetch().
    
    This replaces the dummy vector query with a direct fetch approach:
    1. Fetch Document from database to get chunk_count
    2. Validate user_id ownership
    3. Use chunk_count to reconstruct chunk IDs: f"{doc_id}#chunk{i}"
    4. Use Pinecone index.fetch() to retrieve chunks in order
    
    Args:
        user_id: The user ID for ownership validation
        doc_id: The document ID
        
    Returns:
        List of text chunks in deterministic order
        
    Raises:
        ValueError: If document not found or user doesn't own the document
    """
    db = SessionLocal()
    try:
        # 1. Fetch Document from database and validate ownership
        document = get_document_with_owner(db, doc_id, user_id)
        
        if not document:
            raise ValueError(f"Document not found or access denied for doc_id: {doc_id}")
        
        chunk_count = document.chunk_count
        
        if chunk_count == 0:
            return []
        
        # 2. Reconstruct chunk IDs deterministically
        chunk_ids = [f"{doc_id}#chunk{i}" for i in range(chunk_count)]
        
        # 3. Fetch chunks from Pinecone using index.fetch()
        fetch_response = index.fetch(
            ids=chunk_ids,
            namespace=str(user_id)
        )
        
        # 4. Retrieve chunks in deterministic order (by chunk index)
        chunks: List[str] = []
        for i in range(chunk_count):
            chunk_id = f"{doc_id}#chunk{i}"
            if chunk_id in fetch_response.vectors:
                chunk_text = fetch_response.vectors[chunk_id].metadata.get("text", "")
                chunks.append(chunk_text)
            else:
                # Log warning for missing chunks but continue
                print(f"Warning: Chunk {chunk_id} not found in Pinecone")
        
        return chunks
        
    finally:
        db.close()
