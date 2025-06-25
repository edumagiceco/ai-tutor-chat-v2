from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AILevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class UserRole(str, enum.Enum):
    user = "user"  # 일반 사용자
    institution_admin = "institution_admin"  # 기관 관리자
    super_admin = "super_admin"  # 슈퍼 관리자


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    job_title = Column(String(100))
    department = Column(String(100))
    ai_level = Column(Enum(AILevel), default=AILevel.beginner)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    institution_id = Column(String(100))  # 기관 관리자가 속한 기관 ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reports = relationship("Report", back_populates="creator")