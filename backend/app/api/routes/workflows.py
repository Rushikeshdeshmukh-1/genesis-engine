"""
Simplified workflow orchestration without Temporal.
Uses simple async task execution with database-backed status tracking.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import asyncio
import logging
from datetime import datetime

from app.config import settings
from app.database import AsyncSessionLocal
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.research_agent import ResearchAgent
from app.agents.scoring_agent import ScoringAgent
from app.models.idea import Idea
from sqlalchemy import select

logger = logging.getLogger(__name__)
router = APIRouter()


# Simple in-memory task tracking (in production, use database)
workflow_status = {}


class WorkflowRequest(BaseModel):
    """Request schema for workflow execution."""
    idea_count: int = 10
    category: Optional[str] = None
    auto_research: bool = True
    auto_score: bool = True
    auto_rank: bool = True
    auto_report: bool = True


async def execute_pipeline(workflow_id: str, request: WorkflowRequest):
    """
    Execute the complete pipeline in the background.
    
    This will:
    1. Generate ideas
    2. Research each idea (if enabled)
    3. Score each idea (if enabled)
    4. Rank all ideas (if enabled)
    5. Generate reports (if enabled)
    """
    try:
        logger.info(f"Starting pipeline workflow {workflow_id}")
        workflow_status[workflow_id] = {
            "status": "running",
            "current_step": "idea_generation",
            "progress": 0,
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Step 1: Generate Ideas
        logger.info(f"[{workflow_id}] Step 1: Generating {request.idea_count} ideas")
        workflow_status[workflow_id]["current_step"] = "idea_generation"
        workflow_status[workflow_id]["progress"] = 10
        
        idea_generator = IdeaGeneratorAgent()
        ideas_data = await idea_generator.generate_ideas(
            count=request.idea_count,
            category=request.category
        )
        
        # Save ideas to database
        idea_ids = []
        async with AsyncSessionLocal() as db:
            for idea_data in ideas_data:
                idea = Idea(
                    title=idea_data["title"],
                    description=idea_data["description"],
                    category=idea_data.get("category"),
                    status="generated"
                )
                db.add(idea)
                await db.flush()
                idea_ids.append(idea.id)
            await db.commit()
        
        logger.info(f"[{workflow_id}] Generated {len(idea_ids)} ideas")
        workflow_status[workflow_id]["progress"] = 30
        workflow_status[workflow_id]["ideas_generated"] = len(idea_ids)
        
        # Step 2: Research Ideas (if enabled)
        if request.auto_research:
            logger.info(f"[{workflow_id}] Step 2: Researching ideas")
            workflow_status[workflow_id]["current_step"] = "research"
            workflow_status[workflow_id]["progress"] = 40
            
            research_agent = ResearchAgent()
            for i, idea_id in enumerate(idea_ids):
                try:
                    await research_agent.research_idea(idea_id)
                    progress = 40 + int((i + 1) / len(idea_ids) * 20)
                    workflow_status[workflow_id]["progress"] = progress
                except Exception as e:
                    logger.error(f"[{workflow_id}] Research failed for idea {idea_id}: {e}")
        
        # Step 3: Score Ideas (if enabled)
        if request.auto_score:
            logger.info(f"[{workflow_id}] Step 3: Scoring ideas")
            workflow_status[workflow_id]["current_step"] = "scoring"
            workflow_status[workflow_id]["progress"] = 70
            
            scoring_agent = ScoringAgent()
            for i, idea_id in enumerate(idea_ids):
                try:
                    await scoring_agent.score_idea(idea_id)
                    progress = 70 + int((i + 1) / len(idea_ids) * 20)
                    workflow_status[workflow_id]["progress"] = progress
                except Exception as e:
                    logger.error(f"[{workflow_id}] Scoring failed for idea {idea_id}: {e}")
        
        # Step 4: Rank Ideas (if enabled)
        if request.auto_rank:
            logger.info(f"[{workflow_id}] Step 4: Ranking ideas")
            workflow_status[workflow_id]["current_step"] = "ranking"
            workflow_status[workflow_id]["progress"] = 95
            
            # Simple ranking by overall_score
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Idea).order_by(Idea.overall_score.desc())
                )
                ranked_ideas = result.scalars().all()
                for rank, idea in enumerate(ranked_ideas, 1):
                    idea.rank = rank
                await db.commit()
        
        # Complete
        workflow_status[workflow_id] = {
            "status": "completed",
            "current_step": "completed",
            "progress": 100,
            "ideas_generated": len(idea_ids),
            "completed_at": datetime.utcnow().isoformat()
        }
        logger.info(f"[{workflow_id}] Pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"[{workflow_id}] Pipeline failed: {e}", exc_info=True)
        workflow_status[workflow_id] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        }


@router.post("/pipeline", response_model=dict)
async def trigger_pipeline(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Trigger the complete idea generation and evaluation pipeline.
    
    This will:
    1. Generate ideas
    2. Research each idea
    3. Score each idea
    4. Rank all ideas
    5. Generate reports
    """
    try:
        # Generate unique workflow ID
        workflow_id = f"idea-pipeline-{uuid.uuid4()}"
        
        # Start workflow in background
        background_tasks.add_task(execute_pipeline, workflow_id, request)
        
        return {
            "message": "Pipeline workflow triggered successfully",
            "workflow_id": workflow_id,
            "status": "running",
            "steps": {
                "idea_generation": "pending",
                "research": "pending" if request.auto_research else "skipped",
                "scoring": "pending" if request.auto_score else "skipped",
                "ranking": "pending" if request.auto_rank else "skipped",
                "report_generation": "pending" if request.auto_report else "skipped"
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to trigger pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger pipeline: {str(e)}")


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a running workflow.
    """
    if workflow_id not in workflow_status:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    return {
        "workflow_id": workflow_id,
        **workflow_status[workflow_id]
    }
