from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models.research import ResearchArtifact, CompetitorAnalysis, MarketResearch
from app.agents.research_agent import ResearchAgent

router = APIRouter()


# Pydantic schemas
class ResearchRequest(BaseModel):
    """Request schema for research."""
    idea_id: uuid.UUID
    research_types: List[str] = ["competitor", "market", "trend", "tech"]


class ResearchArtifactResponse(BaseModel):
    """Response schema for research artifact."""
    id: uuid.UUID
    idea_id: uuid.UUID
    research_type: str
    title: str
    summary: str
    confidence_score: int
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/start", response_model=dict)
async def start_research(
    request: ResearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start research for an idea.
    """
    try:
        # Initialize research agent
        agent = ResearchAgent()
        
        # Perform research
        results = await agent.research_idea(
            idea_id=request.idea_id,
            research_types=request.research_types
        )
        
        return {
            "message": "Research started successfully",
            "idea_id": str(request.idea_id),
            "research_count": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start research: {str(e)}")


@router.get("/{idea_id}", response_model=List[ResearchArtifactResponse])
async def get_research(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all research artifacts for an idea.
    """
    query = select(ResearchArtifact).where(ResearchArtifact.idea_id == idea_id)
    result = await db.execute(query)
    artifacts = result.scalars().all()
    
    return [ResearchArtifactResponse.from_orm(artifact) for artifact in artifacts]


@router.get("/{idea_id}/competitors")
async def get_competitors(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get competitor analysis for an idea.
    """
    query = select(CompetitorAnalysis).where(CompetitorAnalysis.idea_id == idea_id)
    result = await db.execute(query)
    competitors = result.scalars().all()
    
    return [
        {
            "id": str(comp.id),
            "name": comp.competitor_name,
            "url": comp.competitor_url,
            "description": comp.description,
            "market_position": comp.market_position,
            "strengths": comp.strengths,
            "weaknesses": comp.weaknesses
        }
        for comp in competitors
    ]


@router.get("/{idea_id}/market")
async def get_market_research(
    idea_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get market research for an idea.
    """
    query = select(MarketResearch).where(MarketResearch.idea_id == idea_id)
    result = await db.execute(query)
    market = result.scalar_one_or_none()
    
    if not market:
        raise HTTPException(status_code=404, detail="Market research not found")
    
    return {
        "id": str(market.id),
        "tam": market.total_addressable_market,
        "sam": market.serviceable_addressable_market,
        "som": market.serviceable_obtainable_market,
        "growth_rate": market.market_growth_rate,
        "trends": market.market_trends,
        "drivers": market.market_drivers,
        "barriers": market.market_barriers,
        "target_segments": market.target_segments,
        "confidence_level": market.confidence_level
    }
