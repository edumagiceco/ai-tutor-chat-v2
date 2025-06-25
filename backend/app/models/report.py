from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    user_progress = "user_progress"
    learning_analytics = "learning_analytics" 
    ai_usage = "ai_usage"
    monthly_summary = "monthly_summary"
    custom_report = "custom_report"


class ReportFormat(str, enum.Enum):
    pdf = "pdf"
    excel = "excel"
    csv = "csv"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String(255), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.pending, nullable=False)
    parameters = Column(JSON, nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)
    error_message = Column(Text)
    
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    creator = relationship("User", back_populates="reports")