import json

from app.services.rag.rag_engine import get_relevant_context
from app.services.tools.summarization_service import summarize_document
from app.services.tools.flashcard_service import generate_flashcards
from app.services.tools.topic_service import extract_key_topics
from app.services.tools.study_mode_service import study_mode
from app.services.tools.mind_map_service import generate_mind_map
from app.services.tools.exam_mode_service import exam_mode

# Known action names
ACTIONS = {"CHAT", "SUMMARIZE", "FLASHCARDS", "TOPICS", "STUDY_MODE", "MIND_MAP"}


def dispatch(data: dict) -> dict:
    """
    Route an incoming Kafka message payload to the correct service call.

    Args:
        data: Parsed JSON payload from the Kafka request topic.

    Returns:
        A dict with keys: request_id, answer, sources, status.
    """
    request_id = data.get("request_id")
    action = data.get("action", "CHAT")
    user_id = data.get("user_id")
    conversation_id = data.get("conversation_id")
    doc_id = data.get("doc_id")
    question = data.get("question")
    document_ids_raw = data.get("document_ids")

    # Normalize document_ids to a list
    document_ids = None
    if isinstance(document_ids_raw, list):
        document_ids = document_ids_raw
    elif isinstance(document_ids_raw, str):
        document_ids = document_ids_raw.split(",") if document_ids_raw else None

    answer = ""
    sources = []
    status = "SUCCESS"

    try:
        if action == "CHAT":
            result = get_relevant_context(
                question=question,
                user_id=user_id,
                conversation_id=conversation_id,
                document_ids=document_ids,
            )
            answer = result.get("answer", "")
            sources = result.get("sources", [])

        elif action == "SUMMARIZE":
            answer = summarize_document(user_id, doc_id)

        elif action == "FLASHCARDS":
            flashcards_data = generate_flashcards(user_id, doc_id)
            answer = json.dumps(flashcards_data)

        elif action == "TOPICS":
            answer = json.dumps(extract_key_topics(user_id, doc_id))

        elif action == "STUDY_MODE":
            answer = study_mode(user_id, doc_id)

        elif action == "MIND_MAP":
            answer = generate_mind_map(user_id, doc_id)

        else:
            status = "ERROR"
            answer = f"Unknown action: {action}"

    except Exception as e:
        status = "ERROR"
        answer = f"Error executing action {action}: {str(e)}"
        print(f"Error executing action {action}: {e}")

    return {
        "request_id": request_id,
        "answer": answer,
        "sources": sources,
        "status": status,
    }
