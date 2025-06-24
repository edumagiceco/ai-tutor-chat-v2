from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message, MessageRole


def create_conversation(db: Session, user_id: int, title: Optional[str] = None) -> Conversation:
    session_id = str(uuid4())
    conversation = Conversation(
        user_id=user_id,
        session_id=session_id,
        title=title or "새 대화"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_user_conversations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> List[Conversation]:
    return db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_conversation_by_id(db: Session, conversation_id: int) -> Optional[Conversation]:
    return db.query(Conversation)\
        .filter(Conversation.id == conversation_id)\
        .first()


def add_message_to_conversation(
    db: Session,
    conversation_id: int,
    content: str,
    role: MessageRole
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        content=content,
        role=role
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    limit: int = 50
) -> List[Message]:
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.timestamp.asc())\
        .limit(limit)\
        .all()