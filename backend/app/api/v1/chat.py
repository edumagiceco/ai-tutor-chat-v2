from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.chat import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.services.chat_service import create_conversation, get_user_conversations, get_conversation_by_id, add_message_to_conversation
from app.services.ai_service import get_ai_response

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_new_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = create_conversation(db, current_user.id, conversation_data.title)
    return conversation


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversations = get_user_conversations(db, current_user.id, skip, limit)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Verify conversation ownership
    conversation = get_conversation_by_id(db, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add user message
    user_message = add_message_to_conversation(
        db, conversation_id, message_data.content, MessageRole.user
    )
    
    # Get AI response
    try:
        ai_response_content = await get_ai_response(
            message_data.content,
            conversation.messages,
            current_user
        )
        
        # Add AI response
        ai_message = add_message_to_conversation(
            db, conversation_id, ai_response_content, MessageRole.assistant
        )
        
        return ai_message
    except Exception as e:
        # Log error and return error message
        error_message = add_message_to_conversation(
            db, conversation_id,
            "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            MessageRole.assistant
        )
        return error_message