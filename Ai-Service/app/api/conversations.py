from fastapi import APIRouter, Form

from app.schemas.conversation import ChatResponse, ConversationResponse
from app.services.rag.memory_service import create_conversation
from app.services.rag.rag_engine import get_relevant_context

router = APIRouter(tags=["conversations"])


# ─────────────────────────────────────────────
# Create Conversation
# ─────────────────────────────────────────────

@router.post("/conversation", response_model=ConversationResponse)
async def start_conversation(user_id: str = Form(...)):
    conversation_id = create_conversation(user_id)
    return ConversationResponse(conversation_id=conversation_id)


# ─────────────────────────────────────────────
# Chat (With RAG + Memory)
# ─────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(
    user_id: str = Form(...),
    conversation_id: str = Form(...),
    question: str = Form(...),
    document_ids: str = Form(None),
):
    doc_id_list = document_ids.split(",") if document_ids else None

    result = get_relevant_context(
        question=question,
        user_id=user_id,
        conversation_id=conversation_id,
        document_ids=doc_id_list,
    )

    return ChatResponse(answer=result["answer"], sources=result["sources"])
