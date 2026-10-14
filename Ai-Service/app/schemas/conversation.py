from pydantic import BaseModel
from typing import List, Optional


class ConversationResponse(BaseModel):
    conversation_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
