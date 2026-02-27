from sqlalchemy.orm import Session
from app.models.document import Document
from app.db import SessionLocal


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_document(db: Session, doc_id: str, user_id: str, chunk_count: int) -> Document:
    """Create a new document record."""
    document = Document(
        id=doc_id,
        user_id=user_id,
        chunk_count=chunk_count
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document_by_id(db: Session, doc_id: str) -> Document:
    """Get document by ID."""
    return db.query(Document).filter(Document.id == doc_id).first()


def get_document_with_owner(db: Session, doc_id: str, user_id: str) -> Document:
    """Get document by ID and validate user ownership."""
    return db.query(Document).filter(
        Document.id == doc_id,
        Document.user_id == user_id
    ).first()
