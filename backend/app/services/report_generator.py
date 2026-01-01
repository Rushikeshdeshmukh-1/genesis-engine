"""
Simplified Report generation service for creating Markdown reports.
"""

import logging
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
import uuid

from app.services.llm_service import LLMService
from app.database import AsyncSessionLocal
from app.models.idea import Idea
from app.models.score import IdeaScore
from app.models.report import IdeaReport, ReportFormat, ReportStatus
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Service for generating idea reports."""
    
    def __init__(self):
        self.llm = LLMService()
        self.output_dir = Path(settings.report_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_report(
        self,
        idea_id: uuid.UUID,
        format: ReportFormat = ReportFormat.MARKDOWN,
        report_type: str = "comprehensive"
    ) -> IdeaReport:
        """
        Generate a report for an idea.
        
        Args:
            idea_id: ID of the idea
            format: Report format (only Markdown supported)
            report_type: Type of report
            
        Returns:
            Generated report
        """
        logger.info(f"Generating {format} report for idea {idea_id}")
        
        start_time = datetime.utcnow()
        
        async with AsyncSessionLocal() as db:
            # Get idea and score
            idea = await self._get_idea(db, idea_id)
            score = await self._get_score(db, idea_id)
            
            # Generate report content (simplified, faster)
            content = await self._generate_content_fast(idea, score)
            
            # Create report record
            report = IdeaReport(
                idea_id=idea_id,
                title=f"{idea.title} - Business Analysis Report",
                report_type=report_type,
                format=format,
                status=ReportStatus.GENERATING,
                executive_summary=content.get("executive_summary"),
                opportunity_analysis=content.get("opportunity_analysis"),
                risk_assessment=content.get("risk_assessment"),
                competitor_overview=content.get("competitor_overview"),
                revenue_models=content.get("revenue_models"),
                tech_stack_recommendation=content.get("tech_stack"),
                score_summary=content.get("score_summary"),
                final_recommendation=content.get("final_recommendation")
            )
            
            db.add(report)
            await db.flush()
            
            # Generate markdown file
            file_path = await self._generate_markdown(report, content, idea, score)
            
            # Update report
            report.file_path = str(file_path) if file_path else None
            report.status = ReportStatus.COMPLETED
            report.completed_at = datetime.utcnow()
            report.generation_duration_seconds = int(
                (datetime.utcnow() - start_time).total_seconds()
            )
            
            if file_path:
                report.file_size_bytes = file_path.stat().st_size
            
            await db.commit()
            await db.refresh(report)
            
            logger.info(f"Report generated successfully: {file_path}")
            return report
    
    async def _get_idea(self, db, idea_id: uuid.UUID) -> Idea:
        """Get idea from database."""
        query = select(Idea).where(Idea.id == idea_id)
        result = await db.execute(query)
        idea = result.scalar_one_or_none()
        if not idea:
            raise ValueError(f"Idea {idea_id} not found")
        return idea
    
    async def _get_score(self, db, idea_id: uuid.UUID) -> Optional[IdeaScore]:
        """Get score from database."""
        query = select(IdeaScore).where(IdeaScore.idea_id == idea_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _generate_content_fast(
        self,
        idea: Idea,
        score: Optional[IdeaScore]
    ) -> Dict[str, str]:
        """Generate report content quickly using a single LLM call."""
        
        # Build a concise prompt for faster generation
        prompt = f"""Create a concise business analysis report for this idea:

**Idea**: {idea.title}
**Description**: {idea.description}
**Category**: {idea.category}
**Overall Score**: {score.overall_score if score else 'Not scored'}

Generate a brief report with these sections (2-3 sentences each):

1. Executive Summary
2. Market Opportunity
3. Key Risks
4. Competitive Landscape
5. Revenue Potential
6. Recommendation (Go/No-Go)

Return as JSON with keys: executive_summary, opportunity_analysis, risk_assessment, competitor_overview, revenue_models, final_recommendation
"""
        
        try:
            content = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.5,  # Lower temperature for more focused output
                max_tokens=1000   # Limit tokens for faster generation
            )
            
            # Add score summary
            if score:
                content["score_summary"] = f"""
**Overall Score**: {score.overall_score:.1f}/100

**Category Scores**:
- Market Demand: {score.market_demand_score:.1f}
- Technical Feasibility: {score.technical_feasibility_score:.1f}
- Revenue Potential: {score.revenue_potential_score:.1f}
- Scalability: {score.scalability_score:.1f}
"""
            else:
                content["score_summary"] = "Not yet scored"
            
            # Add tech stack from idea
            if hasattr(idea, 'tech_stack') and idea.tech_stack:
                content["tech_stack"] = str(idea.tech_stack)
            else:
                content["tech_stack"] = "To be determined"
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to generate report content: {e}")
            # Return fallback content
            return {
                "executive_summary": f"Business analysis report for {idea.title}",
                "opportunity_analysis": idea.description or "Analysis pending",
                "risk_assessment": "Assessment pending",
                "competitor_overview": "Overview pending",
                "revenue_models": "Models pending",
                "tech_stack": "Recommendations pending",
                "score_summary": f"Overall Score: {score.overall_score if score else 'N/A'}",
                "final_recommendation": "Further analysis recommended"
            }
    
    async def _generate_markdown(
        self,
        report: IdeaReport,
        content: Dict[str, str],
        idea: Idea,
        score: Optional[IdeaScore]
    ) -> Path:
        """Generate Markdown report."""
        
        markdown_content = f"""# {report.title}

**Generated**: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Idea ID**: {idea.id}  
**Category**: {idea.category}  
**Status**: {idea.status}

---

## Executive Summary

{content.get("executive_summary", "")}

---

## Market Opportunity

{content.get("opportunity_analysis", "")}

---

## Risk Assessment

{content.get("risk_assessment", "")}

---

## Competitive Landscape

{content.get("competitor_overview", "")}

---

## Revenue Models

{content.get("revenue_models", "")}

---

## Technology Stack

{content.get("tech_stack", "")}

---

## Scoring Summary

{content.get("score_summary", "")}

---

## Final Recommendation

{content.get("final_recommendation", "")}

---

## Idea Details

**Title**: {idea.title}  
**Description**: {idea.description}  
**Problem Statement**: {idea.problem_statement or "N/A"}  
**Target Audience**: {idea.target_audience or "N/A"}  
**Value Proposition**: {idea.value_proposition or "N/A"}  
**Industry**: {idea.industry or "N/A"}  
**Tags**: {", ".join(idea.tags) if idea.tags else "N/A"}

---

*This report was automatically generated by the Idea Engine AI system.*
"""
        
        file_path = self.output_dir / f"report_{report.id}.md"
        file_path.write_text(markdown_content, encoding="utf-8")
        
        logger.info(f"Markdown report saved to {file_path}")
        return file_path
