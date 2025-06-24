from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ToolDifficulty(str, enum.Enum):
    basic = "basic"
    intermediate = "intermediate"
    advanced = "advanced"


class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_category = Column(String(100), nullable=False)
    current_level = Column(Integer, default=1)
    progress = Column(DECIMAL(5, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="learning_paths")


class AITool(Base):
    __tablename__ = "ai_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    difficulty = Column(Enum(ToolDifficulty), nullable=False)
    description = Column(Text)
    usage_guide = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())