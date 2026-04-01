from sqlalchemy import desc, func as sql_func
from app.db import SessionLocal
from app.models.message import Message
from app.models.conversation import Conversation
from app.models.conversation_summary import ConversationSummary


# ─────────────────────────────────────────────
# Conversation Management
# ─────────────────────────────────────────────

def create_conversation(user_id: str) -> str:
    db = SessionLocal()
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    db.close()
    return str(conversation.id)


# ─────────────────────────────────────────────
# Message Persistence
# ─────────────────────────────────────────────

def save_message(conversation_id: str, role: str, content: str):
    db = SessionLocal()
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.close()


def get_recent_messages(conversation_id: str, limit: int = 4):
    """
    Returns the most recent `limit` messages in chronological order.
    Default is 4 (last 2 exchanges) when summary mode is active.
    """
    db = SessionLocal()
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(limit)
        .all()
    )
    db.close()
    return list(reversed(messages))


def get_message_count(conversation_id: str) -> int:
    """Returns total number of messages stored in this conversation."""
    db = SessionLocal()
    count = (
        db.query(sql_func.count(Message.id))
        .filter(Message.conversation_id == conversation_id)
        .scalar()
    )
    db.close()
    return count or 0


def get_old_messages_for_compression(conversation_id: str, keep_recent: int = 4):
    """
    Returns all messages EXCEPT the most recent `keep_recent` ones.
    These older messages are candidates for Gemini compression.
    """
    db = SessionLocal()
    all_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    db.close()

    # Exclude the most recent `keep_recent` messages
    if len(all_messages) <= keep_recent:
        return []
    return all_messages[:-keep_recent]


# ─────────────────────────────────────────────
# Smart Memory Compression
# ─────────────────────────────────────────────

def get_conversation_summary(conversation_id: str) -> str | None:
    """
    Returns the existing Gemini-generated summary for this conversation,
    or None if no summary has been generated yet.
    """
    db = SessionLocal()
    record = (
        db.query(ConversationSummary)
        .filter(ConversationSummary.conversation_id == conversation_id)
        .first()
    )
    db.close()
    return record.summary if record else None


def save_conversation_summary(conversation_id: str, summary_text: str):
    """
    Upserts the conversation summary. Creates if not exists, updates if exists.
    """
    db = SessionLocal()
    record = (
        db.query(ConversationSummary)
        .filter(ConversationSummary.conversation_id == conversation_id)
        .first()
    )

    if record:
        record.summary = summary_text
    else:
        record = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary_text
        )
        db.add(record)

    db.commit()
    db.close()


# ─────────────────────────────────────────────
# Consolidated RAG Memory Loader
# ─────────────────────────────────────────────

def get_rag_memory_context(conversation_id: str, recent_limit: int = 4) -> tuple:
    """
    Fetch recent messages, total message count, and conversation summary
    in a single DB session to minimise round-trips during a RAG request.

    Returns:
        (recent_messages, total_count, summary_or_None)
    """
    db = SessionLocal()
    try:
        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(recent_limit)
            .all()
        )
        total_count = (
            db.query(sql_func.count(Message.id))
            .filter(Message.conversation_id == conversation_id)
            .scalar()
        ) or 0
        summary_record = (
            db.query(ConversationSummary)
            .filter(ConversationSummary.conversation_id == conversation_id)
            .first()
        )
        summary = summary_record.summary if summary_record else None
        return list(reversed(recent_messages)), total_count, summary
    finally:
        db.close()