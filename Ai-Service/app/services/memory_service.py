from sqlalchemy import desc
from app.db import SessionLocal
from app.models.message import Message
from app.models.conversation import Conversation


def create_conversation(user_id: str):
    db = SessionLocal()
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    db.close()
    return str(conversation.id)


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


def get_recent_messages(conversation_id: str, limit: int = 6):
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