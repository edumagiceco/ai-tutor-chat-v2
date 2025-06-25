from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ContentType(str, enum.Enum):
    article = "article"
    tutorial = "tutorial"
    guide = "guide"
    faq = "faq"
    announcement = "announcement"
    policy = "policy"


class ContentStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"
    scheduled = "scheduled"


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    content_type = Column(SQLEnum(ContentType), default=ContentType.article)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.draft)
    
    # Content fields
    summary = Column(Text)
    content = Column(Text, nullable=False)
    featured_image = Column(String(500))
    
    # SEO fields
    meta_title = Column(String(255))
    meta_description = Column(Text)
    meta_keywords = Column(String(500))
    
    # Organization
    category_id = Column(Integer, ForeignKey("content_categories.id"))
    tags = Column(JSON)  # Array of tag strings
    
    # Publishing
    author_id = Column(Integer, ForeignKey("users.id"))
    published_at = Column(DateTime)
    scheduled_at = Column(DateTime)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("contents.id"))
    
    # Analytics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("ContentCategory", back_populates="contents")
    author = relationship("User")
    versions = relationship("Content", backref="parent", remote_side=[id])


class ContentCategory(Base):
    __tablename__ = "content_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("content_categories.id"))
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contents = relationship("Content", back_populates="category")
    children = relationship("ContentCategory", backref="parent", remote_side=[id])