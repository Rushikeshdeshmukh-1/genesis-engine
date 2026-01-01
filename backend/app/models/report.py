from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.database import Base


class ReportFormat(str, enum.Enum):
    """Report format types."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class IdeaReport(Base):
    """Generated reports for ideas."""
    
    __tablename__ = "idea_reports"
    __table_args__ = (
        Index("idx_reports_idea_id", "idea_id"),
        Index("idx_reports_status", "status"),
        Index("idx_reports_created_at", "created_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    
    # Report metadata
    title = Column(String(500), nullable=False)
    report_type = Column(String(100), default="comprehensive")  # comprehensive, summary, executive
    format = Column(SQLEnum(ReportFormat), nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)
    
    # Report content
    executive_summary = Column(Text)
    opportunity_analysis = Column(Text)
    risk_assessment = Column(Text)
    competitor_overview = Column(Text)
    revenue_models = Column(Text)
    tech_stack_recommendation = Column(Text)
    score_summary = Column(Text)
    final_recommendation = Column(Text)
    
    # File storage
    file_path = Column(String(1000))  # Local file path
    storage_url = Column(String(1000))  # MinIO URL
    file_size_bytes = Column(Integer)
    
    # Generation metadata
    template_used = Column(String(200))
    generation_params = Column(String(1000))
    
    # Performance metrics
    generation_duration_seconds = Column(Integer)
    
    # Error tracking
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<IdeaReport(id={self.id}, idea_id={self.idea_id}, format={self.format}, status={self.status})>"
