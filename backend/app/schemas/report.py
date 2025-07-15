from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ReportType(str, Enum):
    user_progress = "user_progress"
    learning_analytics = "learning_analytics"
    ai_usage = "ai_usage"
    monthly_summary = "monthly_summary"
    custom_report = "custom_report"


class ReportFormat(str, Enum):
    pdf = "pdf"
    excel = "excel"
    csv = "csv"


class ReportStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ReportParameters(BaseModel):
    date_from: Optional[str] = None  # Changed to str to handle JSON serialization
    date_to: Optional[str] = None    # Changed to str to handle JSON serialization
    user_ids: Optional[List[int]] = []
    institution_id: Optional[int] = None
    user_scope: Optional[str] = "all"  # all, institution, individual
    include_details: bool = True
    include_charts: bool = True
    custom_filters: Optional[Dict[str, Any]] = {}


class ReportGenerateRequest(BaseModel):
    report_type: ReportType
    format: ReportFormat = ReportFormat.pdf
    parameters: ReportParameters


class ReportBase(BaseModel):
    report_type: ReportType
    title: str
    format: ReportFormat
    status: ReportStatus
    parameters: ReportParameters
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None


class ReportCreate(ReportBase):
    created_by: int


class ReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class ReportResponse(ReportBase):
    id: int
    created_by: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int
    skip: int
    limit: int


class ReportProgressResponse(BaseModel):
    report_id: int
    status: ReportStatus
    progress: int  # 0-100
    message: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds