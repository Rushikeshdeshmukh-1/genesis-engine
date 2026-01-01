from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime
import uuid
import logging

from app.database import get_db
from app.models.idea import Idea
from app.agents.idea_generator import IdeaGeneratorAgent
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic schemas
class IdeaGenerationRequest(BaseModel):
    """Request schema for idea generation."""
    count: int = Field(default=20, ge=1, le=100, description="Number of ideas to generate")
    category: Optional[str] = Field(default=None, description="Specific category to focus on")
    trends: Optional[List[str]] = Field(default=None, description="Trends to consider")
    filters: Optional[dict] = Field(default=None, description="Custom filters")


class IdeaResponse(BaseModel):
    """Response schema for a single idea."""
    id: uuid.UUID
    title: str
    description: str
    problem_statement: Optional[str]
    target_audience: Optional[str]
    value_proposition: Optional[str]
    category: Optional[str]
    tags: List[str]
    industry: Optional[str]
    status: str
    overall_score: Optional[float]
    rank: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IdeaListResponse(BaseModel):
    """Response schema for idea list."""
    ideas: List[IdeaResponse]
    total: int
    page: int
    page_size: int


@router.post("/generate", response_model=dict)
async def generate_ideas(
    request: IdeaGenerationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new business ideas using the LLM agent.
    Ideas are automatically scored after generation.
    """
    try:
        # Initialize idea generator agent
        agent = IdeaGeneratorAgent()
        
        # Generate ideas
        ideas = await agent.generate_ideas(
            count=request.count,
            category=request.category,
            trends=request.trends or [],
            filters=request.filters or {}
        )
        
        # Store ideas in database
        db_ideas = []
        for idea_data in ideas:
            # Convert complex fields to strings if needed
            target_audience = idea_data.get("target_audience")
            if isinstance(target_audience, (dict, list)):
                import json
                target_audience = json.dumps(target_audience)
            
            value_proposition = idea_data.get("value_proposition")
            if isinstance(value_proposition, (dict, list)):
                import json
                value_proposition = json.dumps(value_proposition)
            
            problem_statement = idea_data.get("problem_statement")
            if isinstance(problem_statement, (dict, list)):
                import json
                problem_statement = json.dumps(problem_statement)
            
            db_idea = Idea(
                title=idea_data["title"],
                description=idea_data["description"],
                problem_statement=problem_statement,
                target_audience=target_audience,
                value_proposition=value_proposition,
                category=idea_data.get("category"),
                tags=idea_data.get("tags", []),
                industry=idea_data.get("industry"),
                tech_stack=idea_data.get("tech_stack"),
                estimated_complexity=idea_data.get("estimated_complexity"),
                generation_prompt=idea_data.get("generation_prompt"),
                generation_params=request.dict(),
                status="generated"
            )
            db.add(db_idea)
            db_ideas.append(db_idea)
        
        await db.commit()
        
        # NEW: Automatically score generated ideas
        from app.agents.scoring_agent import ScoringAgent
        scoring_agent = ScoringAgent()
        
        scored_count = 0
        for db_idea in db_ideas:
            try:
                logger.info(f"Auto-scoring idea: {db_idea.title}")
                await scoring_agent.score_idea(db_idea.id)
                scored_count += 1
            except Exception as e:
                logger.warning(f"Auto-scoring failed for {db_idea.id}: {e}")
                # Continue even if scoring fails for one idea
        
        logger.info(f"Auto-scored {scored_count}/{len(db_ideas)} ideas")
        
        return {
            "message": f"Successfully generated {len(db_ideas)} ideas",
            "count": len(db_ideas),
            "idea_ids": [str(idea.id) for idea in db_ideas],
            "scored_count": scored_count
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate ideas: {str(e)}")


@router.get("/", response_model=IdeaListResponse)
async def list_ideas(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category: Optional[str] = None,
    min_score: Optional[float] = None,
    sort_by: str = Query("created_at", regex="^(created_at|overall_score|rank)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all ideas with pagination and filtering.
    """
    # Build query
    query = select(Idea)
    
    # Apply filters
    if status:
        query = query.where(Idea.status == status)
    if category:
        query = query.where(Idea.category == category)
    if min_score is not None:
        query = query.where(Idea.overall_score >= min_score)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply sorting
    sort_column = getattr(Idea, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    ideas = result.scalars().all()
    
    return IdeaListResponse(
        ideas=[IdeaResponse.from_orm(idea) for idea in ideas],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific idea by ID.
    """
    query = select(Idea).where(Idea.id == idea_id)
    result = await db.execute(query)
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return IdeaResponse.from_orm(idea)


@router.delete("/{idea_id}")
async def delete_idea(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an idea by ID.
    """
    query = select(Idea).where(Idea.id == idea_id)
    result = await db.execute(query)
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    await db.delete(idea)
    await db.commit()
    
    return {"message": "Idea deleted successfully", "id": str(idea_id)}


@router.get("/stats/summary")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Get summary statistics about ideas.
    """
    # Total ideas
    total_query = select(func.count(Idea.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Ideas by status
    status_query = select(Idea.status, func.count(Idea.id)).group_by(Idea.status)
    status_result = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_result}
    
    # Average score
    avg_score_query = select(func.avg(Idea.overall_score)).where(Idea.overall_score.isnot(None))
    avg_score_result = await db.execute(avg_score_query)
    avg_score = avg_score_result.scalar()
    
    return {
        "total_ideas": total,
        "by_status": by_status,
        "average_score": float(avg_score) if avg_score else None
    }
