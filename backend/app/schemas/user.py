from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.models.user import AILevel, UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    ai_level: AILevel = AILevel.beginner
    role: UserRole = UserRole.user
    institution_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    ai_level: Optional[AILevel] = None
    role: Optional[UserRole] = None
    institution_id: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    password_hash: str