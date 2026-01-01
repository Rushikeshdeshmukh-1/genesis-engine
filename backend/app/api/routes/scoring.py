from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models.score import IdeaScore
from app.agents.scoring_agent import ScoringAgent

router = APIRouter()


# Pydantic schemas
class ScoringRequest(BaseModel):
    """Request schema for scoring."""
    idea_id: uuid.UUID


class ScoreResponse(BaseModel):
    """Response schema for scores."""
    id: uuid.UUID
    idea_id: uuid.UUID
    overall_score: float
    normalized_score: float
    market_demand_score: float
    competition_score: float
    trend_strength_score: float
    revenue_potential_score: float
    tech_feasibility_score: float
    cost_to_build_score: float
    risk_level_score: float
    user_adoption_score: float
    scalability_score: float
    innovation_score: float
    moat_strength_score: float
    operational_complexity_score: float
    time_to_market_score: float
    team_requirements_score: float
    social_impact_score: float
    global_expansion_score: float
    
    class Config:
        from_attributes = True


@router.post("/score", response_model=dict)
async def score_idea(
    request: ScoringRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Score an idea using the 1000-factor scoring engine.
    """
    try:
        # Initialize scoring agent
        agent = ScoringAgent()
        
        # Score the idea
        score_result = await agent.score_idea(idea_id=request.idea_id)
        
        return {
            "message": "Idea scored successfully",
            "idea_id": str(request.idea_id),
            "overall_score": score_result["overall_score"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to score idea: {str(e)}")


@router.get("/{idea_id}", response_model=ScoreResponse)
async def get_score(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scoring results for an idea.
    """
    query = select(IdeaScore).where(IdeaScore.idea_id == idea_id)
    result = await db.execute(query)
    score = result.scalar_one_or_none()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return ScoreResponse.from_orm(score)


@router.get("/{idea_id}/breakdown")
async def get_score_breakdown(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed factor breakdown for an idea's score.
    """
    query = select(IdeaScore).where(IdeaScore.idea_id == idea_id)
    result = await db.execute(query)
    score = result.scalar_one_or_none()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return {
        "idea_id": str(idea_id),
        "overall_score": score.overall_score,
        "categories": {
            "market_demand": score.market_demand_score,
            "competition": score.competition_score,
            "trend_strength": score.trend_strength_score,
            "revenue_potential": score.revenue_potential_score,
            "tech_feasibility": score.tech_feasibility_score,
            "cost_to_build": score.cost_to_build_score,
            "risk_level": score.risk_level_score,
            "user_adoption": score.user_adoption_score,
            "scalability": score.scalability_score,
            "innovation": score.innovation_score,
            "moat_strength": score.moat_strength_score,
            "operational_complexity": score.operational_complexity_score,
            "time_to_market": score.time_to_market_score,
            "team_requirements": score.team_requirements_score,
            "social_impact": score.social_impact_score,
            "global_expansion": score.global_expansion_score
        },
        "factor_scores": score.factor_scores
    }
