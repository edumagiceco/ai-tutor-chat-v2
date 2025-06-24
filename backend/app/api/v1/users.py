from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate
from app.services.user_service import update_user

router = APIRouter()


@router.get("/profile", response_model=UserSchema)
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.put("/profile", response_model=UserSchema)
async def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    updated_user = update_user(db, current_user, user_update)
    return updated_user