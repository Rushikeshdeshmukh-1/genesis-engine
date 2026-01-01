"""
Research Agent for deep idea research using web scraping and LLM analysis.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
import uuid

from app.services.local_llm_service import local_llm_service
from app.services.scraper_service import ScraperService
from app.database import AsyncSessionLocal
from app.models.idea import Idea
from app.models.research import ResearchArtifact, CompetitorAnalysis, MarketResearch
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Agent for researching business ideas."""
    
    def __init__(self):
        self.llm = local_llm_service
        
    async def research_idea(
        self,
        idea_id: uuid.UUID,
        research_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform comprehensive research on an idea.
        
        Args:
            idea_id: ID of the idea to research
            research_types: Types of research to perform
            
        Returns:
            List of research results
        """
        if research_types is None:
            research_types = ["competitor", "market", "trend", "tech"]
        
        logger.info(f"Starting research for idea {idea_id}")
        
        # Get idea from database
        async with AsyncSessionLocal() as db:
            query = select(Idea).where(Idea.id == idea_id)
            result = await db.execute(query)
            idea = result.scalar_one_or_none()
            
            if not idea:
                raise ValueError(f"Idea {idea_id} not found")
            
            results = []
            
            # Perform each type of research
            if "competitor" in research_types:
                competitor_results = await self._research_competitors(idea, db)
                results.extend(competitor_results)
            
            if "market" in research_types:
                market_results = await self._research_market(idea, db)
                results.append(market_results)
            
            if "trend" in research_types:
                trend_results = await self._research_trends(idea, db)
                results.append(trend_results)
            
            if "tech" in research_types:
                tech_results = await self._research_technology(idea, db)
                results.append(tech_results)
            
            # Update idea status
            idea.status = "researched"
            idea.researched_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Completed research for idea {idea_id}: {len(results)} artifacts")
            return results
    
    async def _research_competitors(
        self,
        idea: Idea,
        db
    ) -> List[Dict[str, Any]]:
        """Research competitors for the idea using web scraping."""
        logger.info(f"Researching competitors for: {idea.title}")
        
        # Build search query for competitors
        search_query = f"{idea.title} {idea.category} competitors alternatives similar products"
        
        # Use web scraping to find real competitors
        from app.services.scraper_service import ScraperService
        
        scraped_competitors = []
        try:
            async with ScraperService() as scraper:
                # Search Google for competitors
                search_results = await scraper.search_google(search_query, num_results=5)
                
                logger.info(f"Found {len(search_results)} competitors from web search")
                
                # Extract competitor data from search results
                for result in search_results:
                    competitor_data = {
                        'name': result.get('title', 'Unknown'),
                        'url': result.get('url'),
                        'description': result.get('snippet', ''),
                        'source': 'web_search'
                    }
                    
                    # Try to scrape the competitor website for more details
                    if competitor_data['url']:
                        try:
                            company_info = await scraper.extract_company_info(competitor_data['url'])
                            competitor_data.update(company_info)
                        except Exception as e:
                            logger.warning(f"Failed to scrape {competitor_data['url']}: {e}")
                    
                    scraped_competitors.append(competitor_data)
        
        except Exception as e:
            logger.warning(f"Web scraping failed, falling back to LLM: {e}")
        
        # Enhance scraped data with LLM analysis
        prompt = f"""Analyze these competitors found via web search for this business idea:

Title: {idea.title}
Description: {idea.description}
Category: {idea.category}

Competitors found:
{json.dumps(scraped_competitors, indent=2)}

For each competitor, provide:
1. Key strengths
2. Key weaknesses  
3. Market position (leader/challenger/niche)
4. Differentiation opportunities for our idea

Return as JSON array with enhanced competitor data."""
        
        try:
            analysis = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.5
            )
            
            # Parse enhanced competitors
            if isinstance(analysis, dict) and "competitors" in analysis:
                enhanced_competitors = analysis["competitors"]
            elif isinstance(analysis, list):
                enhanced_competitors = analysis
            else:
                enhanced_competitors = scraped_competitors  # Fallback to scraped data
            
            # Store competitor analyses
            results = []
            for i, comp_data in enumerate(enhanced_competitors[:5]):  # Limit to 5
                # Merge scraped data with LLM analysis
                if i < len(scraped_competitors):
                    comp_data.update(scraped_competitors[i])
                
                competitor = CompetitorAnalysis(
                    idea_id=idea.id,
                    competitor_name=comp_data.get("name", "Unknown"),
                    competitor_url=comp_data.get("url"),
                    description=comp_data.get("description"),
                    strengths=comp_data.get("strengths", []),
                    weaknesses=comp_data.get("weaknesses", []),
                    market_position=comp_data.get("market_position", "unknown"),
                    differentiation_opportunities=comp_data.get("differentiation", [])
                )
                db.add(competitor)
                results.append(comp_data)
            
            # Create research artifact
            artifact = ResearchArtifact(
                idea_id=idea.id,
                research_type="competitor",
                title=f"Competitor Analysis for {idea.title}",
                summary=f"Found {len(results)} competitors via web search",
                findings={"competitors": results, "search_query": search_query},
                confidence_score=85  # Higher confidence with real data
            )
            db.add(artifact)
            
            return results
        
        except Exception as e:
            logger.error(f"Competitor research failed: {e}")
            return []
    
    async def _research_market(self, idea: Idea, db) -> Dict[str, Any]:
        """Research market size and opportunity."""
        logger.info(f"Researching market for: {idea.title}")
        
        prompt = f"""Analyze the market opportunity for this business idea:

Title: {idea.title}
Description: {idea.description}
Industry: {idea.industry}
Target Audience: {idea.target_audience}

Provide:
1. Total Addressable Market (TAM) estimate
2. Serviceable Addressable Market (SAM) estimate
3. Serviceable Obtainable Market (SOM) estimate
4. Market growth rate
5. Key market trends (list)
6. Market drivers (list)
7. Market barriers (list)
8. Target customer segments (list)
9. Key customer pain points (list)
10. Confidence level (high/medium/low)

Return as JSON."""
        
        try:
            market_data = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.5
            )
            
            # Store market research
            market_research = MarketResearch(
                idea_id=idea.id,
                total_addressable_market=market_data.get("tam", "Unknown"),
                serviceable_addressable_market=market_data.get("sam", "Unknown"),
                serviceable_obtainable_market=market_data.get("som", "Unknown"),
                market_growth_rate=market_data.get("growth_rate", "Unknown"),
                market_trends=market_data.get("trends", []),
                market_drivers=market_data.get("drivers", []),
                market_barriers=market_data.get("barriers", []),
                target_segments=market_data.get("segments", []),
                customer_pain_points=market_data.get("pain_points", []),
                confidence_level=market_data.get("confidence_level", "medium")
            )
            db.add(market_research)
            
            # Create research artifact
            artifact = ResearchArtifact(
                idea_id=idea.id,
                research_type="market",
                title=f"Market Analysis for {idea.title}",
                summary=f"TAM: {market_data.get('tam')}, Growth: {market_data.get('growth_rate')}",
                findings=market_data,
                confidence_score=70
            )
            db.add(artifact)
            
            return market_data
        
        except Exception as e:
            logger.error(f"Market research failed: {e}")
            return {}
    
    async def _research_trends(self, idea: Idea, db) -> Dict[str, Any]:
        """Research relevant trends."""
        logger.info(f"Researching trends for: {idea.title}")
        
        prompt = f"""Identify current trends relevant to this business idea:

Title: {idea.title}
Description: {idea.description}
Category: {idea.category}

Provide:
1. Technology trends (list)
2. Market trends (list)
3. Consumer behavior trends (list)
4. Regulatory trends (list)
5. Trend strength assessment (strong/moderate/weak)

Return as JSON."""
        
        try:
            trend_data = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.6
            )
            
            # Create research artifact
            artifact = ResearchArtifact(
                idea_id=idea.id,
                research_type="trend",
                title=f"Trend Analysis for {idea.title}",
                summary=f"Identified {len(trend_data.get('technology_trends', []))} tech trends",
                findings=trend_data,
                confidence_score=65
            )
            db.add(artifact)
            
            return trend_data
        
        except Exception as e:
            logger.error(f"Trend research failed: {e}")
            return {}
    
    async def _research_technology(self, idea: Idea, db) -> Dict[str, Any]:
        """Research technology feasibility."""
        logger.info(f"Researching technology for: {idea.title}")
        
        prompt = f"""Analyze the technical feasibility of this business idea:

Title: {idea.title}
Description: {idea.description}
Proposed Tech Stack: {idea.tech_stack}

Provide:
1. Technical feasibility score (0-100)
2. Required technologies (list)
3. Technical challenges (list)
4. Alternative tech stacks (list)
5. Development complexity (low/medium/high)
6. Estimated development time
7. Key technical risks (list)

Return as JSON."""
        
        try:
            tech_data = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.5
            )
            
            # Create research artifact
            artifact = ResearchArtifact(
                idea_id=idea.id,
                research_type="tech",
                title=f"Technical Feasibility for {idea.title}",
                summary=f"Feasibility: {tech_data.get('feasibility_score')}/100",
                findings=tech_data,
                confidence_score=80
            )
            db.add(artifact)
            
            return tech_data
        
        except Exception as e:
            logger.error(f"Technology research failed: {e}")
            return {}
