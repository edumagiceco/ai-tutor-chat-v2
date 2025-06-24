from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.conversation import MessageRole


class MessageBase(BaseModel):
    content: str
    role: MessageRole


class MessageCreate(BaseModel):
    content: str


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    session_id: str
    created_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True