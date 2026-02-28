from app.repositories.chunk_repository import get_document_chunks
from app.services.summarization_service import summarize_document as generate_summary
from app.services.flashcard_service import generate_flashcards as create_flashcards
from app.services.topic_extraction_service import extract_key_topics
from app.services.study_mode_service import study_mode as generate_study_mode
from app.services.mind_map_service import generate_mind_map as create_mind_map


def get_all_document_chunks(user_id: str, doc_id: str, top_k: int = 1000):
    """
    Retrieve all document chunks deterministically.

    Note: top_k parameter is kept for compatibility but ignored,
    as we now fetch all chunks in deterministic order.
    """
    return get_document_chunks(user_id, doc_id)


def summarize_document(user_id: str, doc_id: str):
    """
    Generate a structured document summary.

    Delegates to summarization_service for clean separation of concerns.
    Uses Map-Reduce pattern with Gemini 2.5 Flash model.
    """
    return generate_summary(user_id, doc_id)


def generate_flashcards(user_id: str, doc_id: str, num_cards: int = 10):
    """
    Generate flashcards from document content.

    Delegates to flashcard_service for clean separation of concerns.
    Uses Gemini 2.5 Flash model.
    """
    return create_flashcards(user_id, doc_id, num_cards)


def extract_key_topic(user_id: str, doc_id: str):
    """
    Extract important topics and definitions from document content.

    Delegates to topic_extraction_service for clean separation of concerns.
    Uses Gemini 2.5 Flash model.
    """
    return extract_key_topics(user_id, doc_id)


def study_mode(user_id: str, doc_id: str):
    """
    Generate study mode explanation for exam preparation.

    Delegates to study_mode_service for clean separation of concerns.
    Uses Gemini 2.5 Flash model.
    """
    return generate_study_mode(user_id, doc_id)

def generate_mind_map(user_id: str, doc_id: str):
    """
    Generate a mind map from document content.

    Delegates to mind_map_service for clean separation of concerns.
    Uses Gemini 2.5 Flash model and outputs PlantUML.
    """
    return create_mind_map(user_id, doc_id)
