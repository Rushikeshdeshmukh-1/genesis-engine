"""
Temporal activities for the idea pipeline.
"""

from temporalio import activity
import logging
import uuid

from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.research_agent import ResearchAgent
from app.agents.scoring_agent import ScoringAgent
from app.services.ranking_service import RankingService
from app.services.report_generator import ReportGenerator
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@activity.defn
async def generate_ideas_activity(params: dict) -> dict:
    """
    Activity to generate business ideas.
    
    Args:
        params: Generation parameters (count, category, etc.)
    
    Returns:
        Dict with generated idea IDs
    """
    activity.logger.info(f"Generating ideas with params: {params}")
    
    try:
        agent = IdeaGeneratorAgent()
        
        ideas = await agent.generate_ideas(
            count=params.get("count", 10),
            category=params.get("category"),
            trends=params.get("trends", []),
            filters=params.get("filters", {})
        )
        
        # Store in database
        from app.models.idea import Idea
        async with AsyncSessionLocal() as db:
            idea_ids = []
            for idea_data in ideas:
                db_idea = Idea(
                    title=idea_data["title"],
                    description=idea_data["description"],
                    problem_statement=idea_data.get("problem_statement"),
                    target_audience=idea_data.get("target_audience"),
                    value_proposition=idea_data.get("value_proposition"),
                    category=idea_data.get("category"),
                    tags=idea_data.get("tags", []),
                    industry=idea_data.get("industry"),
                    tech_stack=idea_data.get("tech_stack"),
                    estimated_complexity=idea_data.get("estimated_complexity"),
                    generation_params=params,
                    status="generated"
                )
                db.add(db_idea)
                await db.flush()
                idea_ids.append(str(db_idea.id))
            
            await db.commit()
        
        activity.logger.info(f"Generated {len(idea_ids)} ideas")
        return {"idea_ids": idea_ids, "count": len(idea_ids)}
    
    except Exception as e:
        activity.logger.error(f"Idea generation failed: {e}")
        raise


@activity.defn
async def research_idea_activity(params: dict) -> dict:
    """
    Activity to research a business idea.
    
    Args:
        params: Research parameters (idea_id, research_types)
    
    Returns:
        Research results
    """
    idea_id = uuid.UUID(params["idea_id"])
    research_types = params.get("research_types", ["competitor", "market", "trend", "tech"])
    
    activity.logger.info(f"Researching idea {idea_id}")
    
    try:
        agent = ResearchAgent()
        results = await agent.research_idea(idea_id, research_types)
        
        activity.logger.info(f"Completed research for idea {idea_id}")
        return {"idea_id": str(idea_id), "artifacts_count": len(results)}
    
    except Exception as e:
        activity.logger.error(f"Research failed for idea {idea_id}: {e}")
        raise


@activity.defn
async def score_idea_activity(params: dict) -> dict:
    """
    Activity to score a business idea.
    
    Args:
        params: Scoring parameters (idea_id)
    
    Returns:
        Scoring results
    """
    idea_id = uuid.UUID(params["idea_id"])
    
    activity.logger.info(f"Scoring idea {idea_id}")
    
    try:
        agent = ScoringAgent()
        result = await agent.score_idea(idea_id)
        
        activity.logger.info(f"Scored idea {idea_id}: {result['overall_score']:.2f}")
        return result
    
    except Exception as e:
        activity.logger.error(f"Scoring failed for idea {idea_id}: {e}")
        raise


@activity.defn
async def rank_ideas_activity() -> dict:
    """
    Activity to rank all scored ideas.
    
    Returns:
        Ranking results
    """
    activity.logger.info("Ranking all ideas")
    
    try:
        async with AsyncSessionLocal() as db:
            service = RankingService()
            ranked_ideas = await service.rank_ideas(db)
        
        activity.logger.info(f"Ranked {len(ranked_ideas)} ideas")
        return {"ranked_count": len(ranked_ideas)}
    
    except Exception as e:
        activity.logger.error(f"Ranking failed: {e}")
        raise


@activity.defn
async def generate_report_activity(params: dict) -> dict:
    """
    Activity to generate a report for an idea.
    
    Args:
        params: Report parameters (idea_id, format)
    
    Returns:
        Report generation results
    """
    idea_id = uuid.UUID(params["idea_id"])
    format_type = params.get("format", "markdown")
    
    activity.logger.info(f"Generating {format_type} report for idea {idea_id}")
    
    try:
        from app.models.report import ReportFormat
        
        generator = ReportGenerator()
        report = await generator.generate_report(
            idea_id=idea_id,
            format=ReportFormat(format_type),
            report_type="comprehensive"
        )
        
        activity.logger.info(f"Generated report {report.id} for idea {idea_id}")
        return {
            "idea_id": str(idea_id),
            "report_id": str(report.id),
            "format": format_type
        }
    
    except Exception as e:
        activity.logger.error(f"Report generation failed for idea {idea_id}: {e}")
        raise
