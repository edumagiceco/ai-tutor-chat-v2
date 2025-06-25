from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.content import ContentType, ContentStatus


# Content Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = 0
    is_active: Optional[bool] = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Content Schemas
class ContentBase(BaseModel):
    title: str
    slug: Optional[str] = None
    content_type: ContentType = ContentType.article
    status: ContentStatus = ContentStatus.draft
    summary: Optional[str] = None
    content: str
    featured_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = []
    scheduled_at: Optional[datetime] = None


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content_type: Optional[ContentType] = None
    status: Optional[ContentStatus] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    featured_image: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None


class AuthorInfo(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True


class ContentResponse(ContentBase):
    id: int
    author_id: int
    author: Optional[AuthorInfo] = None
    category: Optional[CategoryResponse] = None
    published_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0
    version: int = 1
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True