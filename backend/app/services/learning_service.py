from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.learning import AITool, LearningPath


def get_ai_tools(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None
) -> List[AITool]:
    query = db.query(AITool)
    if category:
        query = query.filter(AITool.category == category)
    
    return query.offset(skip).limit(limit).all()


def get_user_learning_path(db: Session, user_id: int) -> Optional[LearningPath]:
    return db.query(LearningPath)\
        .filter(LearningPath.user_id == user_id)\
        .first()