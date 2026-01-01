"""
Scoring Agent for evaluating ideas across 1000+ factors.
"""

import logging
from typing import Dict, Any
from datetime import datetime
import uuid
import yaml
from pathlib import Path

from app.services.local_llm_service import local_llm_service
from app.database import AsyncSessionLocal
from app.models.idea import Idea
from app.models.score import IdeaScore, ScoringFactor
from app.models.research import ResearchArtifact
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ScoringAgent:
    """Agent for scoring business ideas using 1000+ factors."""
    
    def __init__(self):
        self.llm = local_llm_service
        self.factors_config = self._load_scoring_factors()
        
    def _load_scoring_factors(self) -> Dict[str, Any]:
        """Load scoring factors from YAML configuration."""
        config_path = Path(settings.scoring_factors_config)
        
        if not config_path.exists():
            logger.warning(f"Scoring factors config not found at {config_path}")
            return {"categories": []}
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    async def score_idea(self, idea_id: uuid.UUID) -> Dict[str, Any]:
        """
        Score an idea across all factors.
        
        Args:
            idea_id: ID of the idea to score
            
        Returns:
            Scoring results
        """
        logger.info(f"Starting scoring for idea {idea_id}")
        
        async with AsyncSessionLocal() as db:
            # Get idea
            query = select(Idea).where(Idea.id == idea_id)
            result = await db.execute(query)
            idea = result.scalar_one_or_none()
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            # Get research artifacts
            research_query = select(ResearchArtifact).where(ResearchArtifact.idea_id == idea_id)
            research_result = await db.execute(research_query)
            research_artifacts = research_result.scalars().all()
            
            # Score each category
            category_scores = {}
            all_factor_scores = {}
            
            for category in self.factors_config.get("categories", []):
                category_name = category["name"]
                logger.info(f"Scoring category: {category_name}")
                
                category_score = await self._score_category(
                    idea=idea,
                    category=category,
                    research_artifacts=research_artifacts
                )
                
                category_scores[category_name] = category_score["score"]
                all_factor_scores[category_name] = category_score["factors"]
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(category_scores)
            
            # Store score in database
            idea_score = IdeaScore(
                idea_id=idea_id,
                overall_score=overall_score,
                normalized_score=min(100, max(0, overall_score)),
                market_demand_score=category_scores.get("Market Demand", 0),
                competition_score=category_scores.get("Competition Analysis", 0),
                trend_strength_score=category_scores.get("Trend Strength", 0),
                revenue_potential_score=category_scores.get("Revenue Potential", 0),
                tech_feasibility_score=category_scores.get("Technical Feasibility", 0),
                cost_to_build_score=category_scores.get("Cost to Build", 0),
                risk_level_score=category_scores.get("Risk Assessment", 0),
                user_adoption_score=category_scores.get("User Adoption", 0),
                scalability_score=category_scores.get("Scalability", 0),
                innovation_score=category_scores.get("Innovation & Uniqueness", 0),
                moat_strength_score=category_scores.get("Competitive Moat", 0),
                operational_complexity_score=category_scores.get("Operational Complexity", 0),
                time_to_market_score=category_scores.get("Time to Market", 0),
                team_requirements_score=category_scores.get("Team Requirements", 0),
                social_impact_score=category_scores.get("Social Impact", 0),
                global_expansion_score=category_scores.get("Global Expansion", 0),
                factor_scores=all_factor_scores,
                scoring_model=settings.ollama_model,
                scoring_version="1.0",
                confidence_score=75.0
            )
            
            db.add(idea_score)
            
            # Update idea
            idea.overall_score = overall_score
            idea.status = "scored"
            idea.scored_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Completed scoring for idea {idea_id}: {overall_score:.2f}")
            
            return {
                "idea_id": str(idea_id),
                "overall_score": overall_score,
                "category_scores": category_scores
            }
    
    async def _score_category(
        self,
        idea: Idea,
        category: Dict[str, Any],
        research_artifacts: list
    ) -> Dict[str, Any]:
        """Score a single category."""
        
        # Prepare context
        research_context = self._prepare_research_context(research_artifacts)
        
        # Build scoring prompt
        prompt = f"""Score this business idea on the "{category['name']}" category.

Idea:
Title: {idea.title}
Description: {idea.description}
Category: {idea.category}
Target Audience: {idea.target_audience}

Research Context:
{research_context}

Category Description: {category['description']}

Evaluate the following factors (score each 0-100):
"""
        
        # Add factors to prompt (limit to 3 per category for speed - total ~48 factors)
        factors = category.get("factors", [])[:3]  # Using 3 factors per category
        for factor in factors:
            prompt += f"\n- {factor['name']}: {factor['description']}"
        
        prompt += """

Return a JSON object with:
1. "category_score": Overall category score (0-100)
2. "reasoning": Brief explanation
3. "factor_scores": Object with each factor code and its score

Example:
{
  "category_score": 75,
  "reasoning": "Strong market demand due to...",
  "factor_scores": {
    "MD001": 85,
    "MD002": 70,
    ...
  }
}
"""
        
        
        try:
            import json
            result_text = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for consistent scoring
                json_mode=True
            )
            
            result = json.loads(result_text)
            
            return {
                "score": result.get("category_score", 50),
                "reasoning": result.get("reasoning", ""),
                "factors": result.get("factor_scores", {})
            }
        
        except Exception as e:
            logger.error(f"Failed to score category {category['name']}: {e}")
            return {
                "score": 50,  # Default neutral score
                "reasoning": f"Scoring failed: {str(e)}",
                "factors": {}
            }
    
    def _prepare_research_context(self, research_artifacts: list) -> str:
        """Prepare research context for scoring."""
        if not research_artifacts:
            return "No research data available."
        
        context = []
        for artifact in research_artifacts[:5]:  # Limit to avoid token overflow
            context.append(f"{artifact.research_type.upper()}: {artifact.summary}")
        
        return "\n".join(context)
    
    def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score."""
        total_score = 0
        total_weight = 0
        
        for category in self.factors_config.get("categories", []):
            category_name = category["name"]
            category_weight = category.get("weight", 1.0)
            
            if category_name in category_scores:
                total_score += category_scores[category_name] * category_weight
                total_weight += category_weight
        
        if total_weight == 0:
            return 0
        
        return total_score / total_weight
