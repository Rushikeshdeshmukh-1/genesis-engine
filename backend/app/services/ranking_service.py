"""
Ranking service for ordering ideas by score.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.models.idea import Idea
from app.models.score import IdeaScore

logger = logging.getLogger(__name__)


class RankingService:
    """Service for ranking ideas."""
    
    async def rank_ideas(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Rank all scored ideas.
        
        Args:
            db: Database session
            
        Returns:
            List of ranked ideas
        """
        logger.info("Ranking all ideas")
        
        # Get all scored ideas
        query = (
            select(Idea, IdeaScore)
            .join(IdeaScore, Idea.id == IdeaScore.idea_id)
            .where(Idea.overall_score.isnot(None))
            .order_by(desc(IdeaScore.overall_score))
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        # Assign ranks
        ranked_ideas = []
        for rank, (idea, score) in enumerate(rows, start=1):
            idea.rank = rank
            
            # Calculate percentile
            percentile = ((len(rows) - rank + 1) / len(rows)) * 100
            score.percentile_rank = percentile
            
            ranked_ideas.append({
                "rank": rank,
                "idea_id": str(idea.id),
                "title": idea.title,
                "overall_score": score.overall_score,
                "percentile": percentile
            })
        
        await db.commit()
        
        logger.info(f"Ranked {len(ranked_ideas)} ideas")
        return ranked_ideas
    
    async def get_top_ideas(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top N ranked ideas."""
        
        query = (
            select(Idea, IdeaScore)
            .join(IdeaScore, Idea.id == IdeaScore.idea_id)
            .where(Idea.rank.isnot(None))
            .order_by(Idea.rank)
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "rank": idea.rank,
                "id": str(idea.id),
                "title": idea.title,
                "description": idea.description,
                "category": idea.category,
                "overall_score": score.overall_score,
                "percentile": score.percentile_rank
            }
            for idea, score in rows
        ]
