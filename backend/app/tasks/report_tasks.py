import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.learning import LearningPath, AITool
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def generate_report_task(self, report_id: int) -> Dict[str, Any]:
    """
    Celery task to generate a report in the background.
    """
    db: Session = SessionLocal()
    
    try:
        # Get report from database
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            logger.error(f"Report {report_id} not found")
            return {"status": "error", "message": "Report not found"}
        
        # Update status to processing
        report.status = ReportStatus.processing
        db.commit()
        
        # Update task progress
        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "데이터 수집 중..."}
        )
        
        # Initialize report generator
        generator = ReportGenerator(db, report)
        
        # Collect data based on report type
        self.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "데이터 분석 중..."}
        )
        
        report_data = generator.collect_data()
        
        # Generate report file
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "리포트 생성 중..."}
        )
        
        file_path = generator.generate_file(report_data)
        
        # Update report record
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "마무리 작업 중..."}
        )
        
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            report.file_path = file_path
            report.file_size = file_size
            report.status = ReportStatus.completed
            report.completed_at = datetime.utcnow()
        else:
            report.status = ReportStatus.failed
            report.error_message = "Failed to generate report file"
        
        db.commit()
        
        return {
            "status": "success",
            "report_id": report_id,
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {str(e)}")
        
        # Update report status to failed
        if report:
            report.status = ReportStatus.failed
            report.error_message = str(e)
            db.commit()
        
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()


@celery_app.task
def cleanup_old_reports() -> Dict[str, Any]:
    """
    Periodic task to clean up old report files.
    """
    db: Session = SessionLocal()
    
    try:
        # Get reports older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        old_reports = db.query(Report).filter(
            Report.created_at < cutoff_date,
            Report.file_path.isnot(None)
        ).all()
        
        deleted_count = 0
        for report in old_reports:
            if report.file_path and os.path.exists(report.file_path):
                try:
                    os.remove(report.file_path)
                    report.file_path = None
                    report.file_size = None
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete file {report.file_path}: {str(e)}")
        
        db.commit()
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()