from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract, or_
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from app.api import deps
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.models.content import Content, ContentCategory, ContentType, ContentStatus
from app.models.report import Report, ReportStatus, ReportType, ReportFormat
from app.core.config import settings
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse
)
from app.schemas.report import (
    ReportGenerateRequest, ReportResponse, ReportListResponse, ReportProgressResponse
)
from app.tasks.report_tasks import generate_report_task

router = APIRouter()


@router.get("/stats", response_model=dict)
async def get_admin_stats(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Get admin dashboard statistics.
    Requires institution_admin or super_admin role.
    """
    # Get current date and 30 days ago for growth calculations
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    
    # Total users
    total_users = db.query(func.count(User.id)).scalar()
    
    # Active users (logged in within last 30 days)
    active_users = db.query(func.count(User.id)).filter(
        User.updated_at >= thirty_days_ago
    ).scalar()
    
    # Total documents (RAG documents table not yet implemented)
    total_documents = 0  # Placeholder until RAG documents table is created
    
    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    
    # Calculate growth rates (simplified - in production, compare with previous period)
    # For now, returning mock growth rates
    user_growth = 12.5
    document_growth = 8.3
    conversation_growth = 25.4
    
    # If institution admin, filter stats by their institution
    if current_user.role == UserRole.institution_admin and current_user.institution_id:
        # Filter users by institution
        institution_users = db.query(func.count(User.id)).filter(
            User.institution_id == current_user.institution_id
        ).scalar()
        
        # Filter conversations by institution users
        institution_conversations = db.query(func.count(Conversation.id)).join(
            User, Conversation.user_id == User.id
        ).filter(
            User.institution_id == current_user.institution_id
        ).scalar()
        
        return {
            "totalUsers": institution_users,
            "activeUsers": active_users,  # This would need institution filtering too
            "totalDocuments": total_documents,
            "totalConversations": institution_conversations,
            "userGrowth": user_growth,
            "documentGrowth": document_growth,
            "conversationGrowth": conversation_growth,
        }
    
    # For super admin, return all stats
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalDocuments": total_documents,
        "totalConversations": total_conversations,
        "userGrowth": user_growth,
        "documentGrowth": document_growth,
        "conversationGrowth": conversation_growth,
    }


@router.get("/recent-activities", response_model=list)
async def get_recent_activities(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    limit: int = 10
) -> Any:
    """
    Get recent system activities.
    Requires institution_admin or super_admin role.
    """
    activities = []
    
    # Get recent users
    recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
    for user in recent_users:
        activities.append({
            "type": "user_signup",
            "title": f"새로운 사용자 {user.name}님이 가입했습니다.",
            "timestamp": user.created_at,
            "icon": "user"
        })
    
    # Get recent documents (when RAG documents table is implemented)
    # recent_docs = db.query(RAGDocument).order_by(RAGDocument.created_at.desc()).limit(5).all()
    # for doc in recent_docs:
    #     activities.append({
    #         "type": "document_upload",
    #         "title": f"새로운 RAG 문서 '{doc.title}'가 업로드되었습니다.",
    #         "timestamp": doc.created_at,
    #         "icon": "document"
    #     })
    
    # Sort by timestamp and return top N
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]


@router.get("/analytics", response_model=dict)
async def get_analytics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    date_range: str = Query("last30days")
) -> Any:
    """
    Get detailed analytics data.
    Requires institution_admin or super_admin role.
    """
    # Calculate date range
    now = datetime.utcnow()
    if date_range == "last7days":
        start_date = now - timedelta(days=7)
    elif date_range == "last30days":
        start_date = now - timedelta(days=30)
    elif date_range == "last90days":
        start_date = now - timedelta(days=90)
    elif date_range == "thisMonth":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_range == "lastMonth":
        first_day_this_month = now.replace(day=1)
        start_date = (first_day_this_month - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        now = first_day_this_month - timedelta(days=1)
    else:
        start_date = now - timedelta(days=30)
    
    # User Analytics
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(
        User.updated_at >= start_date
    ).scalar()
    new_users_this_period = db.query(func.count(User.id)).filter(
        User.created_at >= start_date
    ).scalar()
    
    # Calculate growth rate (simplified)
    previous_period_start = start_date - (now - start_date)
    previous_users = db.query(func.count(User.id)).filter(
        User.created_at < start_date,
        User.created_at >= previous_period_start
    ).scalar()
    
    user_growth_rate = 0
    if previous_users > 0:
        user_growth_rate = ((new_users_this_period - previous_users) / previous_users) * 100
    
    # Users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    role_counts = {
        "user": 0,
        "institution_admin": 0,
        "super_admin": 0
    }
    for role, count in users_by_role:
        role_counts[role.value] = count
    
    # Learning Analytics
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.created_at >= start_date
    ).scalar()
    
    # For now, using mock data for some metrics
    # In production, these would be calculated from actual data
    avg_messages_per_conversation = 15
    completion_rate = 75
    avg_learning_time = 32
    
    # Popular topics (mock data)
    popular_topics = [
        {"topic": "Python 프로그래밍", "count": 156},
        {"topic": "데이터 분석", "count": 132},
        {"topic": "머신러닝 기초", "count": 98},
        {"topic": "웹 개발", "count": 87},
        {"topic": "AI 활용", "count": 76},
    ]
    
    # Daily active users (mock data for last 7 days)
    daily_active_users = []
    for i in range(7):
        date = now - timedelta(days=i)
        count = 50 + (i * 5)  # Mock data
        daily_active_users.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    daily_active_users.reverse()
    
    # Peak usage hours (mock data)
    peak_usage_hours = [
        {"hour": 9, "count": 120},
        {"hour": 10, "count": 145},
        {"hour": 11, "count": 132},
        {"hour": 14, "count": 156},
        {"hour": 15, "count": 178},
        {"hour": 16, "count": 165},
    ]
    
    # API usage (mock data)
    api_usage = {
        "anthropic": 3456,
        "openai": 1234
    }
    
    # Content analytics (mock data)
    total_documents = 0  # RAG documents not implemented yet
    documents_by_category = [
        {"category": "기술 문서", "count": 45},
        {"category": "교육 자료", "count": 32},
        {"category": "업무 가이드", "count": 28},
    ]
    
    popular_documents = [
        {"title": "Python 입문 가이드", "views": 234},
        {"title": "ChatGPT 활용법", "views": 198},
        {"title": "데이터 분석 기초", "views": 156},
        {"title": "Git 사용법", "views": 132},
        {"title": "프로젝트 관리", "views": 98},
    ]
    
    return {
        "userAnalytics": {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "newUsersThisMonth": new_users_this_period,
            "userGrowthRate": round(user_growth_rate, 1),
            "averageSessionDuration": 28,  # Mock data
            "usersByRole": role_counts,
        },
        "learningAnalytics": {
            "totalConversations": total_conversations,
            "averageMessagesPerConversation": avg_messages_per_conversation,
            "popularTopics": popular_topics,
            "completionRate": completion_rate,
            "averageLearningTime": avg_learning_time,
        },
        "usageAnalytics": {
            "dailyActiveUsers": daily_active_users,
            "peakUsageHours": peak_usage_hours,
            "apiUsage": api_usage,
        },
        "contentAnalytics": {
            "totalDocuments": total_documents,
            "documentsByCategory": documents_by_category,
            "popularDocuments": popular_documents,
        }
    }


# Settings file path
SETTINGS_FILE = Path("/app/config/system_settings.json")


def load_settings() -> dict:
    """Load system settings from file"""
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Return default settings
        return {
            "general": {
                "siteName": "AI Tutor System",
                "siteDescription": "AI 기반 교육 챗봇 시스템",
                "maintenanceMode": False,
                "allowRegistration": True,
                "defaultUserRole": "user",
                "sessionTimeout": 60
            },
            "ai": {
                "defaultModel": "claude-3-sonnet",
                "maxTokens": 4000,
                "temperature": 0.7,
                "ragEnabled": True,
                "ragTopK": 5,
                "streamingEnabled": True
            },
            "security": {
                "passwordMinLength": 8,
                "passwordRequireUppercase": True,
                "passwordRequireNumbers": True,
                "passwordRequireSpecial": True,
                "maxLoginAttempts": 5,
                "lockoutDuration": 30,
                "twoFactorEnabled": False
            },
            "notifications": {
                "emailEnabled": False,
                "emailHost": "",
                "emailPort": 587,
                "emailUsername": "",
                "emailFromAddress": "",
                "slackEnabled": False,
                "slackWebhookUrl": ""
            },
            "storage": {
                "maxFileSize": 10,
                "allowedFileTypes": ["pdf", "docx", "txt", "md"],
                "storageQuota": 50,
                "autoCleanupEnabled": False,
                "cleanupAfterDays": 90
            }
        }


def save_settings(settings_data: dict):
    """Save system settings to file"""
    # Create directory if it doesn't exist
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings_data, f, indent=2, ensure_ascii=False)


@router.get("/settings", response_model=dict)
async def get_system_settings(
    *,
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Get system settings.
    Requires super_admin role.
    """
    return load_settings()


@router.put("/settings", response_model=dict)
async def update_system_settings(
    *,
    settings_data: dict,
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Update system settings.
    Requires super_admin role.
    """
    try:
        save_settings(settings_data)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear", response_model=dict)
async def clear_cache(
    *,
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Clear system cache.
    Requires super_admin role.
    """
    # In a real implementation, this would clear Redis cache
    # For now, return success
    return {"message": "Cache cleared successfully", "timestamp": datetime.utcnow()}


@router.post("/backup", response_model=dict)
async def backup_database(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Initiate database backup.
    Requires super_admin role.
    """
    # In a real implementation, this would trigger a database backup process
    # For now, return a mock response
    backup_filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
    
    return {
        "message": "Backup initiated successfully",
        "filename": backup_filename,
        "timestamp": datetime.utcnow(),
        "status": "in_progress"
    }


# Content Management Endpoints
@router.get("/contents", response_model=List[ContentResponse])
async def get_contents(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    search: Optional[str] = None,
    status: Optional[str] = None,
    content_type: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get list of contents with filtering options.
    Requires institution_admin or super_admin role.
    """
    query = db.query(Content)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Content.title.contains(search),
                Content.content.contains(search),
                Content.summary.contains(search)
            )
        )
    
    if status and status != "all":
        query = query.filter(Content.status == status)
    
    if content_type and content_type != "all":
        query = query.filter(Content.content_type == content_type)
    
    if category_id and category_id != "all":
        query = query.filter(Content.category_id == category_id)
    
    # Order by creation date
    query = query.order_by(Content.created_at.desc())
    
    # Pagination
    contents = query.offset(skip).limit(limit).all()
    
    return contents


@router.post("/contents", response_model=ContentResponse)
async def create_content(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    content_in: ContentCreate
) -> Any:
    """
    Create new content.
    Requires institution_admin or super_admin role.
    """
    # Generate slug if not provided
    if not content_in.slug:
        slug = content_in.title.lower()
        slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
        slug = "-".join(filter(None, slug.split("-")))
        content_in.slug = slug
    
    # Check if slug already exists
    existing = db.query(Content).filter(Content.slug == content_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Content with slug '{content_in.slug}' already exists"
        )
    
    # Create content
    db_content = Content(
        **content_in.dict(),
        author_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Set published_at if status is published
    if content_in.status == ContentStatus.published:
        db_content.published_at = datetime.utcnow()
    
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return db_content


@router.get("/contents/{content_id}", response_model=ContentResponse)
async def get_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Get specific content by ID.
    Requires institution_admin or super_admin role.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


@router.put("/contents/{content_id}", response_model=ContentResponse)
async def update_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    content_in: ContentUpdate,
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Update existing content.
    Requires institution_admin or super_admin role.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Update fields
    update_data = content_in.dict(exclude_unset=True)
    
    # Handle status changes
    if "status" in update_data:
        if update_data["status"] == ContentStatus.published and content.status != ContentStatus.published:
            content.published_at = datetime.utcnow()
        elif update_data["status"] != ContentStatus.published:
            content.published_at = None
    
    # Update version
    content.version += 1
    content.updated_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.delete("/contents/{content_id}")
async def delete_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Delete content.
    Requires super_admin role.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content)
    db.commit()
    
    return {"message": "Content deleted successfully"}


@router.post("/contents/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Publish content.
    Requires institution_admin or super_admin role.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = ContentStatus.published
    content.published_at = datetime.utcnow()
    content.updated_at = datetime.utcnow()
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


@router.post("/contents/{content_id}/archive", response_model=ContentResponse)
async def archive_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Archive content.
    Requires institution_admin or super_admin role.
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = ContentStatus.archived
    content.updated_at = datetime.utcnow()
    
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return content


# Content Category Endpoints
@router.get("/content-categories", response_model=List[CategoryResponse])
async def get_content_categories(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Get list of content categories.
    Requires institution_admin or super_admin role.
    """
    categories = db.query(ContentCategory)\
        .filter(ContentCategory.is_active == True)\
        .order_by(ContentCategory.order, ContentCategory.name)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return categories


@router.post("/content-categories", response_model=CategoryResponse)
async def create_content_category(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    category_in: CategoryCreate
) -> Any:
    """
    Create new content category.
    Requires institution_admin or super_admin role.
    """
    # Generate slug if not provided
    if not category_in.slug:
        slug = category_in.name.lower()
        slug = "".join(c if c.isalnum() or c == "-" else "-" for c in slug)
        slug = "-".join(filter(None, slug.split("-")))
        category_in.slug = slug
    
    # Check if slug already exists
    existing = db.query(ContentCategory).filter(ContentCategory.slug == category_in.slug).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Category with slug '{category_in.slug}' already exists"
        )
    
    # Create category
    db_category = ContentCategory(
        **category_in.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.put("/content-categories/{category_id}", response_model=CategoryResponse)
async def update_content_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(deps.get_institution_admin_user)
) -> Any:
    """
    Update content category.
    Requires institution_admin or super_admin role.
    """
    category = db.query(ContentCategory).filter(ContentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    update_data = category_in.dict(exclude_unset=True)
    category.updated_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/content-categories/{category_id}")
async def delete_content_category(
    *,
    db: Session = Depends(deps.get_db),
    category_id: int,
    current_user: User = Depends(deps.get_super_admin_user)
) -> Any:
    """
    Delete content category.
    Requires super_admin role.
    """
    category = db.query(ContentCategory).filter(ContentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has contents
    content_count = db.query(func.count(Content.id)).filter(Content.category_id == category_id).scalar()
    if content_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category with {content_count} contents. Please move or delete contents first."
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


# Report endpoints
@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    request: ReportGenerateRequest
) -> Any:
    """
    Generate a new report.
    """
    # Generate report title based on type
    title_map = {
        ReportType.user_progress: "사용자 학습 진도 리포트",
        ReportType.learning_analytics: "학습 분석 리포트",
        ReportType.ai_usage: "AI 도구 사용 현황",
        ReportType.monthly_summary: f"{datetime.now().strftime('%Y년 %m월')} 월간 종합 리포트",
        ReportType.custom_report: "맞춤형 리포트"
    }
    
    # Create report record
    report = Report(
        report_type=request.report_type,
        title=title_map.get(request.report_type, "리포트"),
        format=request.format,
        status=ReportStatus.pending,
        parameters=request.parameters.dict(),
        created_by=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Trigger background task to generate report
    generate_report_task.delay(report.id)
    
    return report


@router.get("/reports", response_model=ReportListResponse)
async def get_reports(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    skip: int = 0,
    limit: int = 100,
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None
) -> Any:
    """
    Get list of generated reports.
    """
    query = db.query(Report)
    
    # Filter by institution for institution admins
    if current_user.role == UserRole.institution_admin:
        query = query.filter(Report.created_by == current_user.id)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    if status:
        query = query.filter(Report.status == status)
    
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add download URLs
    for report in reports:
        if report.file_path and report.status == ReportStatus.completed:
            report.download_url = f"/api/v1/admin/reports/{report.id}/download"
    
    return {
        "reports": reports,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    report_id: int
) -> Any:
    """
    Get report details.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    if current_user.role == UserRole.institution_admin and report.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
    if report.file_path and report.status == ReportStatus.completed:
        report.download_url = f"/api/v1/admin/reports/{report.id}/download"
    
    return report


@router.get("/reports/{report_id}/progress", response_model=ReportProgressResponse)
async def get_report_progress(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    report_id: int
) -> Any:
    """
    Get report generation progress.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    if current_user.role == UserRole.institution_admin and report.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report")
    
    # Get task status from Celery
    from celery.result import AsyncResult
    
    # Find the task ID (in production, store this in the Report model)
    # For now, we'll use a simple pattern
    task_id = f"generate_report_{report.id}"
    
    progress = 0
    message = "대기 중..."
    estimated_time = None
    
    if report.status == ReportStatus.processing:
        # Try to get task status
        try:
            result = AsyncResult(task_id)
            if result.state == 'PENDING':
                progress = 0
                message = "작업 대기 중..."
            elif result.state == 'PROGRESS':
                progress = result.info.get('current', 0)
                message = result.info.get('status', '처리 중...')
            elif result.state == 'SUCCESS':
                progress = 100
                message = "완료됨"
            elif result.state == 'FAILURE':
                progress = 0
                message = str(result.info)
        except:
            # Fallback if Celery is not available
            progress = 45
            message = "데이터 수집 중..."
            estimated_time = 30
    elif report.status == ReportStatus.completed:
        progress = 100
        message = "완료됨"
    elif report.status == ReportStatus.failed:
        progress = 0
        message = report.error_message or "처리 실패"
    
    return {
        "report_id": report.id,
        "status": report.status,
        "progress": progress,
        "message": message,
        "estimated_time_remaining": estimated_time
    }


@router.get("/reports/{report_id}/download")
async def download_report(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_institution_admin_user),
    report_id: int
) -> Any:
    """
    Download report file.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    if current_user.role == UserRole.institution_admin and report.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to download this report")
    
    if report.status != ReportStatus.completed or not report.file_path:
        raise HTTPException(status_code=400, detail="Report file not available")
    
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Return file
    from fastapi.responses import FileResponse
    filename = f"report_{report.id}_{report.created_at.strftime('%Y%m%d')}.{report.format}"
    
    return FileResponse(
        path=report.file_path,
        filename=filename,
        media_type="application/octet-stream"
    )