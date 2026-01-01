"""
Simple Report Generator Service
Generates business analysis reports in Markdown and HTML formats.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json

from app.models.idea import Idea
from app.models.score import IdeaScore
from app.models.research import ResearchArtifact, CompetitorAnalysis, MarketResearch
from app.services.storage_service import storage_service
from app.database import AsyncSessionLocal
from sqlalchemy import select
import uuid

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Simple report generator for business ideas."""
    
    def __init__(self):
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    async def generate_idea_report(
        self,
        idea_id: uuid.UUID,
        format: str = "markdown"
    ) -> str:
        """
        Generate a comprehensive report for an idea.
        
        Args:
            idea_id: ID of the idea
            format: Report format ('markdown' or 'html')
            
        Returns:
            Path to generated report
        """
        logger.info(f"Generating {format} report for idea {idea_id}")
        
        # Fetch idea and related data
        async with AsyncSessionLocal() as db:
            # Get idea
            result = await db.execute(select(Idea).where(Idea.id == idea_id))
            idea = result.scalars().first()
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            # Get score
            result = await db.execute(select(IdeaScore).where(IdeaScore.idea_id == idea_id))
            score = result.scalars().first()
            
            # Get research artifacts
            result = await db.execute(
                select(ResearchArtifact).where(ResearchArtifact.idea_id == idea_id)
            )
            research = result.scalars().all()
            
            # Get competitor analysis
            result = await db.execute(
                select(CompetitorAnalysis).where(CompetitorAnalysis.idea_id == idea_id)
            )
            competitors = result.scalars().all()
            
            # Get market research
            result = await db.execute(
                select(MarketResearch).where(MarketResearch.idea_id == idea_id)
            )
            market = result.scalars().first()
        
        # Generate report content
        if format == "markdown":
            content = self._generate_markdown_report(idea, score, research, competitors, market)
            filename = f"idea_report_{idea_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        elif format == "html":
            content = self._generate_html_report(idea, score, research, competitors, market)
            filename = f"idea_report_{idea_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save report
        filepath = self.reports_dir / filename
        filepath.write_text(content, encoding='utf-8')
        
        # Also save to storage service
        storage_service.save_report(filename, content.encode('utf-8'))
        
        logger.info(f"Report generated: {filepath}")
        return str(filepath)
    
    def _generate_markdown_report(
        self,
        idea: Idea,
        score: Optional[IdeaScore],
        research: list,
        competitors: list,
        market: Optional[MarketResearch]
    ) -> str:
        """Generate Markdown format report."""
        
        report = f"""# Business Idea Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

### Idea Overview
- **Title**: {idea.title}
- **Category**: {idea.category or 'N/A'}
- **Status**: {idea.status}
- **Overall Score**: {score.overall_score if score else 'Not scored yet'}/100
- **Rank**: #{idea.rank if idea.rank else 'Not ranked yet'}

### Description
{idea.description}

---

## Problem Statement

{idea.problem_statement or 'Not specified'}

---

## Target Audience

{idea.target_audience or 'Not specified'}

---

## Scoring Analysis

"""
        
        if score:
            report += f"""
### Overall Score: {score.overall_score}/100

### Category Breakdown
"""
            if score.category_scores:
                for category, cat_score in score.category_scores.items():
                    report += f"- **{category}**: {cat_score}/100\n"
        else:
            report += "Scoring not yet completed.\n"
        
        report += "\n---\n\n## Market Research\n\n"
        
        if market:
            report += f"""
### Market Size
- **TAM**: {market.total_addressable_market}
- **SAM**: {market.serviceable_addressable_market}
- **SOM**: {market.serviceable_obtainable_market}
- **Growth Rate**: {market.market_growth_rate}

### Market Trends
"""
            for trend in (market.market_trends or []):
                report += f"- {trend}\n"
            
            report += "\n### Market Drivers\n"
            for driver in (market.market_drivers or []):
                report += f"- {driver}\n"
            
            report += "\n### Market Barriers\n"
            for barrier in (market.market_barriers or []):
                report += f"- {barrier}\n"
        else:
            report += "Market research not yet completed.\n"
        
        report += "\n---\n\n## Competitive Analysis\n\n"
        
        if competitors:
            report += f"Found {len(competitors)} competitors:\n\n"
            for i, comp in enumerate(competitors, 1):
                report += f"""
### {i}. {comp.competitor_name}
- **URL**: {comp.competitor_url or 'N/A'}
- **Market Position**: {comp.market_position}

**Strengths**:
"""
                for strength in (comp.strengths or []):
                    report += f"- {strength}\n"
                
                report += "\n**Weaknesses**:\n"
                for weakness in (comp.weaknesses or []):
                    report += f"- {weakness}\n"
                
                report += "\n**Differentiation Opportunities**:\n"
                for opp in (comp.differentiation_opportunities or []):
                    report += f"- {opp}\n"
                
                report += "\n"
        else:
            report += "Competitive analysis not yet completed.\n"
        
        report += "\n---\n\n## Research Artifacts\n\n"
        
        if research:
            for artifact in research:
                report += f"""
### {artifact.title}
- **Type**: {artifact.research_type}
- **Confidence**: {artifact.confidence_score}/100

**Summary**: {artifact.summary}

"""
        else:
            report += "No research artifacts available.\n"
        
        report += f"""
---

## Technical Details

### Proposed Tech Stack
{idea.tech_stack or 'Not specified'}

### Revenue Model
{idea.revenue_model or 'Not specified'}

---

## Metadata

- **Idea ID**: {idea.id}
- **Created**: {idea.created_at.strftime('%Y-%m-%d %H:%M:%S') if idea.created_at else 'N/A'}
- **Last Updated**: {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S') if idea.updated_at else 'N/A'}
- **Researched**: {idea.researched_at.strftime('%Y-%m-%d %H:%M:%S') if idea.researched_at else 'Not yet'}
- **Scored**: {idea.scored_at.strftime('%Y-%m-%d %H:%M:%S') if idea.scored_at else 'Not yet'}

---

*Report generated by Project RDx 00 - Idea Engine*
"""
        
        return report
    
    def _generate_html_report(
        self,
        idea: Idea,
        score: Optional[IdeaScore],
        research: list,
        competitors: list,
        market: Optional[MarketResearch]
    ) -> str:
        """Generate HTML format report."""
        
        # Convert markdown to HTML (simple version)
        markdown_content = self._generate_markdown_report(idea, score, research, competitors, market)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Idea Report - {idea.title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        .score {{
            font-size: 2em;
            color: #27ae60;
            font-weight: bold;
        }}
        .metadata {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        ul {{
            padding-left: 20px;
        }}
        .competitor {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Business Idea Analysis Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Executive Summary</h2>
        <h3>{idea.title}</h3>
        <p><strong>Category:</strong> {idea.category or 'N/A'}</p>
        <p><strong>Status:</strong> {idea.status}</p>
        <p><strong>Overall Score:</strong> <span class="score">{score.overall_score if score else 'N/A'}/100</span></p>
        <p><strong>Rank:</strong> #{idea.rank if idea.rank else 'Not ranked yet'}</p>
        
        <h3>Description</h3>
        <p>{idea.description}</p>
        
        <h2>Problem Statement</h2>
        <p>{idea.problem_statement or 'Not specified'}</p>
        
        <h2>Target Audience</h2>
        <p>{idea.target_audience or 'Not specified'}</p>
        
        <div class="metadata">
            <h3>Metadata</h3>
            <p><strong>Idea ID:</strong> {idea.id}</p>
            <p><strong>Created:</strong> {idea.created_at.strftime('%Y-%m-%d %H:%M:%S') if idea.created_at else 'N/A'}</p>
            <p><strong>Last Updated:</strong> {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S') if idea.updated_at else 'N/A'}</p>
        </div>
        
        <hr>
        <p><em>Report generated by Project RDx 00 - Idea Engine</em></p>
    </div>
</body>
</html>"""
        
        return html


# Global instance
report_generator = ReportGenerator()
