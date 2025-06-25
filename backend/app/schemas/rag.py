"""
Pydantic schemas for RAG endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUpload(BaseModel):
    """Schema for uploading documents"""
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: Optional[str] = Field("guide", description="Category of document")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class DocumentResponse(BaseModel):
    """Response schema for document operations"""
    success: bool
    message: str
    document_ids: List[str] = Field(default_factory=list)


class RAGQuery(BaseModel):
    """Schema for RAG query"""
    question: str = Field(..., description="Question to ask the RAG system")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters for document search")


class RAGResponse(BaseModel):
    """Response schema for RAG query"""
    question: str
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    timestamp: Optional[str] = None


class DocumentDelete(BaseModel):
    """Schema for deleting documents"""
    document_ids: List[str] = Field(..., description="List of document IDs to delete")