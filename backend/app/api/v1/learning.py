from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.learning import AITool, LearningPath
from app.services.learning_service import get_ai_tools, get_user_learning_path

router = APIRouter()


@router.get("/ai-tools")
async def get_tools(
    skip: int = 0,
    limit: int = 50,
    category: str = None,
    db: Session = Depends(get_db)
):
    tools = get_ai_tools(db, skip, limit, category)
    return tools


@router.get("/path")
async def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    path = get_user_learning_path(db, current_user.id)
    return path