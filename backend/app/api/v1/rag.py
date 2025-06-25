"""
RAG (Retrieval-Augmented Generation) API endpoints
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from ...api import deps
from ...models.user import User
from ...schemas.rag import (
    DocumentUpload,
    DocumentResponse,
    RAGQuery,
    RAGResponse,
    DocumentDelete
)
from ...services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_documents(
    document: DocumentUpload,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Upload and index a document for RAG"""
    try:
        # Check if user has permission (optional: add role-based access)
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user cannot upload documents"
            )
        
        # Process document
        metadata = {
            "title": document.title,
            "uploaded_by": current_user.id,
            "category": document.category,
            **document.metadata
        }
        
        document_ids = await rag_service.process_documents(
            texts=[document.content],
            metadata=[metadata]
        )
        
        return DocumentResponse(
            success=True,
            message=f"Successfully uploaded document: {document.title}",
            document_ids=document_ids
        )
        
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/upload-file", response_model=DocumentResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("guide"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Upload a file and index its content for RAG"""
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Process as document
        metadata = {
            "title": title,
            "uploaded_by": current_user.id,
            "filename": file.filename,
            "category": category,
            "source": "file"
        }
        
        document_ids = await rag_service.process_documents(
            texts=[text],
            metadata=[metadata]
        )
        
        return DocumentResponse(
            success=True,
            message=f"Successfully processed file: {file.filename}",
            document_ids=document_ids
        )
        
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/query", response_model=RAGResponse)
async def query_rag(
    query: RAGQuery,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Query the RAG system for answers"""
    try:
        # Perform RAG query
        result = await rag_service.ask(
            question=query.question,
            user_id=current_user.id,
            session_id=query.session_id
        )
        
        return RAGResponse(
            question=result["question"],
            answer=result["answer"],
            sources=result.get("sources", []),
            timestamp=result.get("timestamp")
        )
        
    except Exception as e:
        logger.error(f"Failed to process RAG query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/documents/{document_id}", response_model=Dict[str, Any])
async def delete_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a document from the vector store"""
    try:
        # Check permission (optional: add admin check)
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user cannot delete documents"
            )
        
        # Delete document
        from ...services.vector_service import vector_service
        success = await vector_service.delete_documents([document_id])
        
        if success:
            return {
                "success": True,
                "message": f"Successfully deleted document: {document_id}"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )
            
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents", response_model=Dict[str, Any])
async def get_documents(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get list of documents in the vector store"""
    try:
        # For now, we'll return mock data since we need to implement document tracking
        # In production, you'd store document metadata in the database
        documents = [
            {
                "id": "doc_001",
                "title": "ChatGPT 프롬프트 엔지니어링 가이드",
                "content": "ChatGPT를 효과적으로 활용하기 위한 프롬프트 작성 방법...",
                "category": "tutorial",
                "metadata": {
                    "source": "internal",
                    "author": current_user.name,
                    "created_at": "2024-01-20T10:00:00Z",
                    "updated_at": "2024-01-20T10:00:00Z"
                },
                "chunk_count": 15,
                "embedding_status": "completed"
            },
            {
                "id": "doc_002",
                "title": "Claude AI 사용 가이드",
                "content": "Claude AI의 특징과 활용 방법에 대한 상세 설명...",
                "category": "guide",
                "metadata": {
                    "source": "external",
                    "author": "AI 전문가",
                    "created_at": "2024-01-22T14:30:00Z",
                    "updated_at": "2024-01-22T14:30:00Z"
                },
                "chunk_count": 20,
                "embedding_status": "completed"
            }
        ]
        
        # Filter by category if provided
        if category and category != 'all':
            documents = [doc for doc in documents if doc['category'] == category]
        
        # Apply pagination
        total = len(documents)
        documents = documents[skip:skip + limit]
        
        return {
            "documents": documents,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get a specific document by ID"""
    try:
        # Mock data for now
        document = {
            "id": document_id,
            "title": "ChatGPT 프롬프트 엔지니어링 가이드",
            "content": "ChatGPT를 효과적으로 활용하기 위한 프롬프트 작성 방법...",
            "category": "tutorial",
            "metadata": {
                "source": "internal",
                "author": current_user.name,
                "created_at": "2024-01-20T10:00:00Z",
                "updated_at": "2024-01-20T10:00:00Z"
            },
            "chunk_count": 15,
            "embedding_status": "completed"
        }
        
        return document
        
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )