import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.rl_config
import xlsxwriter
from jinja2 import Template

from app.models.report import Report, ReportType, ReportFormat
from app.models.user import User, UserRole, AILevel
from app.models.conversation import Conversation, Message
from app.models.learning import LearningPath, AITool
from app.core.config import settings


class ReportGenerator:
    def __init__(self, db: Session, report: Report):
        self.db = db
        self.report = report
        self.parameters = report.parameters
        
        # Setup Korean font support for PDF
        self._setup_fonts()
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
        # Create reports directory if not exists
        self.reports_dir = os.path.join(os.path.dirname(__file__), "../../reports")
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _setup_fonts(self):
        """Setup fonts for Korean support."""
        # For now, use default fonts
        # In production, you would register Korean fonts here
        reportlab.rl_config.warnOnMissingFontGlyphs = 0
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#4B5563'),
            spaceAfter=20,
        ))
    
    def collect_data(self) -> Dict[str, Any]:
        """Collect data based on report type."""
        if self.report.report_type == ReportType.user_progress:
            return self._collect_user_progress_data()
        elif self.report.report_type == ReportType.learning_analytics:
            return self._collect_learning_analytics_data()
        elif self.report.report_type == ReportType.ai_usage:
            return self._collect_ai_usage_data()
        elif self.report.report_type == ReportType.monthly_summary:
            return self._collect_monthly_summary_data()
        elif self.report.report_type == ReportType.custom_report:
            return self._collect_custom_report_data()
        else:
            raise ValueError(f"Unknown report type: {self.report.report_type}")
    
    def generate_file(self, data: Dict[str, Any]) -> str:
        """Generate report file based on format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{self.report.id}_{timestamp}"
        
        if self.report.format == ReportFormat.pdf:
            return self._generate_pdf(data, filename)
        elif self.report.format == ReportFormat.excel:
            return self._generate_excel(data, filename)
        elif self.report.format == ReportFormat.csv:
            return self._generate_csv(data, filename)
        else:
            raise ValueError(f"Unknown report format: {self.report.format}")
    
    def _collect_user_progress_data(self) -> Dict[str, Any]:
        """Collect user progress data."""
        # Parse date range
        date_from = self.parameters.get("date_from")
        date_to = self.parameters.get("date_to")
        user_ids = self.parameters.get("user_ids", [])
        
        # Build query
        query = self.db.query(User).join(LearningPath, User.id == LearningPath.user_id, isouter=True)
        
        if user_ids:
            query = query.filter(User.id.in_(user_ids))
        
        if date_from:
            query = query.filter(User.created_at >= date_from)
        if date_to:
            query = query.filter(User.created_at <= date_to)
        
        users = query.all()
        
        # Collect progress data for each user
        user_data = []
        for user in users:
            # Get conversation stats
            conv_count = self.db.query(func.count(Conversation.id)).filter(
                Conversation.user_id == user.id
            ).scalar()
            
            msg_count = self.db.query(func.count(Message.id)).join(
                Conversation
            ).filter(
                Conversation.user_id == user.id,
                Message.role == "user"
            ).scalar()
            
            # Get learning path if exists
            learning_path = self.db.query(LearningPath).filter(
                LearningPath.user_id == user.id
            ).first()
            
            user_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "ai_level": user.ai_level.value if user.ai_level else "beginner",
                "created_at": user.created_at,
                "conversation_count": conv_count,
                "message_count": msg_count,
                "current_level": learning_path.current_level if learning_path else 1,
                "progress": learning_path.progress if learning_path else 0,
            })
        
        # Summary statistics
        total_users = len(user_data)
        avg_conversations = sum(u["conversation_count"] for u in user_data) / total_users if total_users > 0 else 0
        avg_messages = sum(u["message_count"] for u in user_data) / total_users if total_users > 0 else 0
        avg_progress = sum(u["progress"] for u in user_data) / total_users if total_users > 0 else 0
        
        return {
            "users": user_data,
            "summary": {
                "total_users": total_users,
                "avg_conversations": round(avg_conversations, 1),
                "avg_messages": round(avg_messages, 1),
                "avg_progress": round(avg_progress, 1),
                "date_range": {
                    "from": date_from,
                    "to": date_to
                }
            }
        }
    
    def _collect_learning_analytics_data(self) -> Dict[str, Any]:
        """Collect learning analytics data."""
        date_from = self.parameters.get("date_from")
        date_to = self.parameters.get("date_to")
        
        # Build base query
        query = self.db.query(
            User.ai_level,
            func.count(User.id).label("user_count")
        ).group_by(User.ai_level)
        
        if date_from:
            query = query.filter(User.created_at >= date_from)
        if date_to:
            query = query.filter(User.created_at <= date_to)
        
        # Get AI level distribution
        level_distribution = query.all()
        
        # Get popular AI tools
        tool_usage = self.db.query(
            AITool.name,
            AITool.category,
            AITool.difficulty,
            func.count(Message.id).label("usage_count")
        ).select_from(Message).join(
            Conversation
        ).filter(
            Message.content.like(f"%{AITool.name}%")
        ).group_by(
            AITool.id
        ).order_by(
            func.count(Message.id).desc()
        ).limit(10).all()
        
        # Get learning patterns
        hourly_activity = self.db.query(
            func.hour(Message.timestamp).label("hour"),
            func.count(Message.id).label("message_count")
        ).select_from(Message).group_by(
            func.hour(Message.timestamp)
        ).all()
        
        return {
            "level_distribution": [
                {"level": level.value if level else "unknown", "count": count}
                for level, count in level_distribution
            ],
            "popular_tools": [
                {
                    "name": name,
                    "category": category,
                    "difficulty": difficulty,
                    "usage_count": usage_count
                }
                for name, category, difficulty, usage_count in tool_usage
            ],
            "hourly_activity": [
                {"hour": hour, "count": count}
                for hour, count in hourly_activity
            ],
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
    
    def _collect_ai_usage_data(self) -> Dict[str, Any]:
        """Collect AI tool usage data."""
        date_from = self.parameters.get("date_from")
        date_to = self.parameters.get("date_to")
        
        # Get all AI tools
        tools = self.db.query(AITool).all()
        
        tool_stats = []
        for tool in tools:
            # Count mentions in messages
            query = self.db.query(func.count(Message.id)).select_from(Message)
            
            if date_from:
                query = query.filter(Message.timestamp >= date_from)
            if date_to:
                query = query.filter(Message.timestamp <= date_to)
            
            mention_count = query.filter(
                Message.content.like(f"%{tool.name}%")
            ).scalar()
            
            # Count unique users
            unique_users = self.db.query(
                func.count(func.distinct(Conversation.user_id))
            ).select_from(Message).join(
                Conversation
            ).filter(
                Message.content.like(f"%{tool.name}%")
            ).scalar()
            
            tool_stats.append({
                "name": tool.name,
                "category": tool.category,
                "difficulty": tool.difficulty,
                "mention_count": mention_count,
                "unique_users": unique_users,
                "description": tool.description
            })
        
        # Sort by mention count
        tool_stats.sort(key=lambda x: x["mention_count"], reverse=True)
        
        # Category summary
        category_summary = {}
        for tool in tool_stats:
            cat = tool["category"]
            if cat not in category_summary:
                category_summary[cat] = {"count": 0, "mentions": 0}
            category_summary[cat]["count"] += 1
            category_summary[cat]["mentions"] += tool["mention_count"]
        
        return {
            "tools": tool_stats[:20],  # Top 20 tools
            "category_summary": category_summary,
            "total_tools": len(tools),
            "date_range": {
                "from": date_from,
                "to": date_to
            }
        }
    
    def _collect_monthly_summary_data(self) -> Dict[str, Any]:
        """Collect monthly summary data."""
        # Get current month or specified month
        now = datetime.utcnow()
        year = self.parameters.get("year", now.year)
        month = self.parameters.get("month", now.month)
        
        # Calculate date range
        date_from = datetime(year, month, 1)
        if month == 12:
            date_to = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            date_to = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # User statistics
        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= date_from,
            User.created_at <= date_to
        ).scalar()
        
        active_users = self.db.query(
            func.count(func.distinct(Conversation.user_id))
        ).filter(
            Conversation.created_at >= date_from,
            Conversation.created_at <= date_to
        ).scalar()
        
        # Conversation statistics
        total_conversations = self.db.query(
            func.count(Conversation.id)
        ).filter(
            Conversation.created_at >= date_from,
            Conversation.created_at <= date_to
        ).scalar()
        
        total_messages = self.db.query(
            func.count(Message.id)
        ).join(Conversation).filter(
            Message.timestamp >= date_from,
            Message.timestamp <= date_to
        ).scalar()
        
        # Learning progress
        avg_progress = self.db.query(
            func.avg(LearningPath.progress)
        ).filter(
            LearningPath.updated_at >= date_from,
            LearningPath.updated_at <= date_to
        ).scalar() or 0
        
        # Daily activity
        daily_activity = self.db.query(
            func.date(Message.timestamp).label("date"),
            func.count(Message.id).label("message_count")
        ).join(Conversation).filter(
            Message.timestamp >= date_from,
            Message.timestamp <= date_to
        ).group_by(
            func.date(Message.timestamp)
        ).all()
        
        return {
            "summary": {
                "month": f"{year}-{month:02d}",
                "new_users": new_users,
                "active_users": active_users,
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "avg_progress": round(avg_progress, 1)
            },
            "daily_activity": [
                {"date": str(date), "count": count}
                for date, count in daily_activity
            ]
        }
    
    def _collect_custom_report_data(self) -> Dict[str, Any]:
        """Collect custom report data based on parameters."""
        # This is a flexible report type that can be customized
        # For now, return a combination of other data
        user_data = self._collect_user_progress_data()
        analytics_data = self._collect_learning_analytics_data()
        
        return {
            "user_progress": user_data,
            "learning_analytics": analytics_data,
            "custom_parameters": self.parameters
        }
    
    def _generate_pdf(self, data: Dict[str, Any], filename: str) -> str:
        """Generate PDF report."""
        filepath = os.path.join(self.reports_dir, f"{filename}.pdf")
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(self.report.title, self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5 * inch))
        
        # Report info
        info_data = [
            ["생성일:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["생성자:", self.db.query(User).filter(User.id == self.report.created_by).first().name],
            ["리포트 유형:", self.report.report_type.value],
        ]
        
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5 * inch))
        
        # Generate content based on report type
        if self.report.report_type == ReportType.user_progress:
            story.extend(self._generate_user_progress_pdf(data))
        elif self.report.report_type == ReportType.learning_analytics:
            story.extend(self._generate_learning_analytics_pdf(data))
        elif self.report.report_type == ReportType.ai_usage:
            story.extend(self._generate_ai_usage_pdf(data))
        elif self.report.report_type == ReportType.monthly_summary:
            story.extend(self._generate_monthly_summary_pdf(data))
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def _generate_user_progress_pdf(self, data: Dict[str, Any]) -> List:
        """Generate user progress PDF content."""
        story = []
        
        # Summary section
        story.append(Paragraph("요약", self.styles['CustomHeading']))
        summary = data["summary"]
        summary_data = [
            ["총 사용자 수:", f"{summary['total_users']}명"],
            ["평균 대화 수:", f"{summary['avg_conversations']}개"],
            ["평균 메시지 수:", f"{summary['avg_messages']}개"],
            ["평균 진행률:", f"{summary['avg_progress']}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # User details table
        story.append(Paragraph("사용자 상세", self.styles['CustomHeading']))
        
        user_headers = ["이름", "이메일", "부서", "AI 레벨", "대화 수", "진행률"]
        user_data = [[
            user["name"],
            user["email"],
            user["department"] or "-",
            user["ai_level"],
            str(user["conversation_count"]),
            f"{user['progress']}%"
        ] for user in data["users"][:20]]  # First 20 users
        
        if user_data:
            user_table = Table([user_headers] + user_data)
            user_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(user_table)
        
        return story
    
    def _generate_learning_analytics_pdf(self, data: Dict[str, Any]) -> List:
        """Generate learning analytics PDF content."""
        story = []
        
        # Level distribution
        story.append(Paragraph("AI 레벨 분포", self.styles['CustomHeading']))
        level_headers = ["레벨", "사용자 수"]
        level_data = [[item["level"], str(item["count"])] for item in data["level_distribution"]]
        
        if level_data:
            level_table = Table([level_headers] + level_data, colWidths=[2 * inch, 2 * inch])
            level_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(level_table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Popular tools
        story.append(Paragraph("인기 AI 도구", self.styles['CustomHeading']))
        tool_headers = ["도구명", "카테고리", "난이도", "사용 횟수"]
        tool_data = [[
            tool["name"],
            tool["category"],
            tool["difficulty"],
            str(tool["usage_count"])
        ] for tool in data["popular_tools"][:10]]
        
        if tool_data:
            tool_table = Table([tool_headers] + tool_data)
            tool_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tool_table)
        
        return story
    
    def _generate_ai_usage_pdf(self, data: Dict[str, Any]) -> List:
        """Generate AI usage PDF content."""
        story = []
        
        # Summary
        story.append(Paragraph("AI 도구 사용 현황", self.styles['CustomHeading']))
        story.append(Paragraph(f"총 {data['total_tools']}개의 AI 도구 분석", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Top tools
        story.append(Paragraph("상위 사용 도구", self.styles['CustomHeading']))
        tool_headers = ["도구명", "카테고리", "난이도", "언급 횟수", "사용자 수"]
        tool_data = [[
            tool["name"],
            tool["category"],
            tool["difficulty"],
            str(tool["mention_count"]),
            str(tool["unique_users"])
        ] for tool in data["tools"][:15]]
        
        if tool_data:
            tool_table = Table([tool_headers] + tool_data)
            tool_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(tool_table)
        
        return story
    
    def _generate_monthly_summary_pdf(self, data: Dict[str, Any]) -> List:
        """Generate monthly summary PDF content."""
        story = []
        
        summary = data["summary"]
        
        # Summary section
        story.append(Paragraph(f"{summary['month']} 월간 요약", self.styles['CustomHeading']))
        
        summary_data = [
            ["신규 사용자:", f"{summary['new_users']}명"],
            ["활성 사용자:", f"{summary['active_users']}명"],
            ["총 대화 수:", f"{summary['total_conversations']}개"],
            ["총 메시지 수:", f"{summary['total_messages']}개"],
            ["평균 학습 진행률:", f"{summary['avg_progress']}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)
        
        return story
    
    def _generate_excel(self, data: Dict[str, Any], filename: str) -> str:
        """Generate Excel report."""
        filepath = os.path.join(self.reports_dir, f"{filename}.xlsx")
        
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Add formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4B5563',
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            # Create sheets based on report type
            if self.report.report_type == ReportType.user_progress:
                self._create_user_progress_excel(data, writer, header_format)
            elif self.report.report_type == ReportType.learning_analytics:
                self._create_learning_analytics_excel(data, writer, header_format)
            elif self.report.report_type == ReportType.ai_usage:
                self._create_ai_usage_excel(data, writer, header_format)
            elif self.report.report_type == ReportType.monthly_summary:
                self._create_monthly_summary_excel(data, writer, header_format)
        
        return filepath
    
    def _create_user_progress_excel(self, data: Dict[str, Any], writer, header_format):
        """Create user progress Excel sheets."""
        # Summary sheet
        summary_df = pd.DataFrame([data["summary"]])
        summary_df.to_excel(writer, sheet_name='요약', index=False)
        
        # User details sheet
        if data["users"]:
            users_df = pd.DataFrame(data["users"])
            users_df["created_at"] = pd.to_datetime(users_df["created_at"]).dt.strftime('%Y-%m-%d')
            users_df.to_excel(writer, sheet_name='사용자 상세', index=False)
            
            # Format the header
            worksheet = writer.sheets['사용자 상세']
            for col_num, value in enumerate(users_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
    
    def _create_learning_analytics_excel(self, data: Dict[str, Any], writer, header_format):
        """Create learning analytics Excel sheets."""
        # Level distribution
        if data["level_distribution"]:
            level_df = pd.DataFrame(data["level_distribution"])
            level_df.to_excel(writer, sheet_name='레벨 분포', index=False)
        
        # Popular tools
        if data["popular_tools"]:
            tools_df = pd.DataFrame(data["popular_tools"])
            tools_df.to_excel(writer, sheet_name='인기 도구', index=False)
        
        # Hourly activity
        if data["hourly_activity"]:
            activity_df = pd.DataFrame(data["hourly_activity"])
            activity_df.to_excel(writer, sheet_name='시간대별 활동', index=False)
    
    def _create_ai_usage_excel(self, data: Dict[str, Any], writer, header_format):
        """Create AI usage Excel sheets."""
        # Tools sheet
        if data["tools"]:
            tools_df = pd.DataFrame(data["tools"])
            tools_df.to_excel(writer, sheet_name='AI 도구', index=False)
        
        # Category summary
        if data["category_summary"]:
            category_data = [
                {"category": k, "tool_count": v["count"], "total_mentions": v["mentions"]}
                for k, v in data["category_summary"].items()
            ]
            category_df = pd.DataFrame(category_data)
            category_df.to_excel(writer, sheet_name='카테고리 요약', index=False)
    
    def _create_monthly_summary_excel(self, data: Dict[str, Any], writer, header_format):
        """Create monthly summary Excel sheets."""
        # Summary sheet
        summary_df = pd.DataFrame([data["summary"]])
        summary_df.to_excel(writer, sheet_name='월간 요약', index=False)
        
        # Daily activity
        if data["daily_activity"]:
            activity_df = pd.DataFrame(data["daily_activity"])
            activity_df.to_excel(writer, sheet_name='일별 활동', index=False)
    
    def _generate_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Generate CSV report."""
        filepath = os.path.join(self.reports_dir, f"{filename}.csv")
        
        # For CSV, we'll create a flat structure
        flat_data = []
        
        if self.report.report_type == ReportType.user_progress:
            flat_data = data["users"]
        elif self.report.report_type == ReportType.learning_analytics:
            flat_data = data["popular_tools"]
        elif self.report.report_type == ReportType.ai_usage:
            flat_data = data["tools"]
        elif self.report.report_type == ReportType.monthly_summary:
            flat_data = [data["summary"]]
        
        if flat_data:
            df = pd.DataFrame(flat_data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath