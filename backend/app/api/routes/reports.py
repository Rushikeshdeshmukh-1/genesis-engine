from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
import uuid

from app.database import get_db
from app.models.report import IdeaReport, ReportFormat
from app.services.report_generator import ReportGenerator

router = APIRouter()


# Pydantic schemas
class ReportGenerationRequest(BaseModel):
    """Request schema for report generation."""
    idea_id: uuid.UUID
    format: ReportFormat = ReportFormat.PDF
    report_type: str = "comprehensive"


@router.post("/generate", response_model=dict)
async def generate_report(
    request: ReportGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a report for an idea.
    """
    try:
        # Initialize report generator
        generator = ReportGenerator()
        
        # Generate report
        report = await generator.generate_report(
            idea_id=request.idea_id,
            format=request.format,
            report_type=request.report_type
        )
        
        return {
            "message": "Report generated successfully",
            "report_id": str(report.id),
            "idea_id": str(request.idea_id),
            "format": request.format,
            "download_url": f"/api/v1/reports/{report.id}/download"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/{idea_id}/list")
async def list_reports(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    List all reports for an idea.
    """
    query = select(IdeaReport).where(IdeaReport.idea_id == idea_id)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return [
        {
            "id": str(report.id),
            "title": report.title,
            "format": report.format,
            "status": report.status,
            "created_at": report.created_at.isoformat(),
            "download_url": f"/api/v1/reports/{report.id}/download"
        }
        for report in reports
    ]


@router.get("/{report_id}/download")
async def download_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a generated report.
    """
    query = select(IdeaReport).where(IdeaReport.id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Determine media type
    media_type = "application/pdf" if report.format == ReportFormat.PDF else "text/markdown"
    
    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=f"idea_report_{report.idea_id}.{report.format.value}"
    )
