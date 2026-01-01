"""
Idea Generator Agent using LLM to create business ideas.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import random

from app.services.local_llm_service import local_llm_service

logger = logging.getLogger(__name__)

# Diverse categories for idea generation
DIVERSE_CATEGORIES = [
    "SaaS", "Marketplace", "AI/ML", "FinTech", "HealthTech",
    "EdTech", "PropTech", "AgriTech", "CleanTech", "FoodTech",
    "LogisticsTech", "HRTech", "LegalTech", "InsurTech", "RetailTech",
    "Gaming", "Entertainment", "Social Media", "E-commerce", "B2B Tools"
]

# Trending topics to inject for diversity
TRENDING_TOPICS = [
    "AI automation", "Blockchain", "Sustainability", "Remote work",
    "Mental health", "Personalization", "Privacy", "Web3",
    "Climate tech", "Accessibility", "Gig economy", "Creator economy",
    "Decentralization", "Green energy", "Digital health", "Smart cities",
    "Cybersecurity", "Data analytics", "IoT", "Quantum computing"
]


class IdeaGeneratorAgent:
    """Agent for generating tech business ideas."""
    
    def __init__(self):
        self.llm = local_llm_service
        
    def _build_generation_prompt(
        self,
        count: int,
        category: Optional[str] = None,
        trends: List[str] = None,
        filters: Dict[str, Any] = None
    ) -> str:
        """Build the prompt for idea generation with diversity."""
        
        # Inject random trends if not provided
        if not trends or len(trends) == 0:
            trends = random.sample(TRENDING_TOPICS, k=min(3, len(TRENDING_TOPICS)))
        
        # Add random category constraint for diversity if not specified
        if not category:
            category = random.choice(DIVERSE_CATEGORIES)
        
        base_prompt = f"""Generate {count} innovative, feasible tech business ideas in the {category} category.

Each idea should:
- Address a real problem or pain point
- Be technically buildable with current technology
- Have a clear target audience
- Offer unique value proposition
- Be commercially viable

IMPORTANT: Generate completely UNIQUE and CREATIVE ideas. 
- Avoid common patterns like "Uber for X" or "Airbnb for Y"
- Think unconventionally and creatively
- Each idea should be distinctly different from others
- Focus on novel solutions and approaches

"""
        
        if trends and len(trends) > 0:
            base_prompt += f"\nConsider these current trends: {', '.join(trends)}\n"
        
        if filters:
            base_prompt += f"\nAdditional constraints: {json.dumps(filters)}\n"
        
        base_prompt += """
Return a JSON array of ideas with this exact structure:
[
  {
    "title": "Concise, catchy title",
    "description": "2-3 sentence description of the idea",
    "problem_statement": "What problem does this solve?",
    "target_audience": "Who is this for?",
    "value_proposition": "Why would customers choose this?",
    "category": "Category (e.g., SaaS, Marketplace, AI/ML, FinTech, HealthTech, etc.)",
    "tags": ["tag1", "tag2", "tag3"],
    "industry": "Primary industry",
    "tech_stack": {
      "frontend": ["technology1", "technology2"],
      "backend": ["technology1", "technology2"],
      "infrastructure": ["technology1", "technology2"]
    },
    "estimated_complexity": "low|medium|high"
  }
]

Generate exactly {count} unique, high-quality ideas that are DIFFERENT from each other.
"""
        
        return base_prompt
    
    async def generate_ideas(
        self,
        count: int = 20,
        category: Optional[str] = None,
        trends: List[str] = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate business ideas using the LLM.
        
        Args:
            count: Number of ideas to generate
            category: Optional category to focus on
            trends: Optional list of trends to consider
            filters: Optional additional filters
            
        Returns:
            List of generated ideas
        """
        logger.info(f"Generating {count} ideas (category={category})")
        
        try:
            # Optimize: Generate in smaller batches for faster response
            # Instead of generating 20 ideas at once (4+ minutes), 
            # generate 5 at a time (much faster)
            batch_size = 5
            all_ideas = []
            
            # Calculate number of batches needed
            num_batches = (count + batch_size - 1) // batch_size
            
            for batch_num in range(num_batches):
                # Calculate how many ideas for this batch
                remaining = count - len(all_ideas)
                current_batch_size = min(batch_size, remaining)
                
                logger.info(f"Generating batch {batch_num + 1}/{num_batches} ({current_batch_size} ideas)")
                
                # Build prompt for this batch
                prompt = self._build_generation_prompt(current_batch_size, category, trends, filters)
                
                # System prompt
                system_prompt = """You are an expert business analyst and entrepreneur with deep knowledge of technology trends, market opportunities, and startup ecosystems. 

You excel at identifying genuine market needs and creating innovative solutions. Your ideas are:
- Practical and implementable
- Based on real market research and trends
- Technically feasible with current technology
- Commercially viable with clear revenue models
- Differentiated from existing solutions

Always provide detailed, well-thought-out ideas in valid JSON format."""
                
                # Vary temperature for diversity (higher = more creative)
                temperature = random.uniform(0.85, 0.95)
                
                # Generate ideas for this batch
                response_text = await self.llm.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    json_mode=True
                )
                
                # Parse JSON response
                response = json.loads(response_text)
                
                # Parse response - generate_json already returns parsed JSON
                # Response should be a list of idea dicts
                ideas = []
                if isinstance(response, list):
                    # Direct list of ideas
                    ideas = response
                elif isinstance(response, dict):
                    # Could be wrapped in various keys
                    if "ideas" in response:
                        ideas = response["ideas"]
                    elif len(response) == 1:
                        # Single key dict, get the value
                        key = list(response.keys())[0]
                        value = response[key]
                        if isinstance(value, list):
                            ideas = value
                        else:
                            # Single idea as dict
                            ideas = [response]
                    else:
                        # Treat the whole dict as a single idea
                        ideas = [response]
                else:
                    logger.warning(f"Unexpected response type in batch {batch_num + 1}: {type(response)}")
                    ideas = []
                
                # Filter out non-dict items and add metadata
                valid_ideas = []
                for idea in ideas:
                    if isinstance(idea, dict) and "title" in idea:
                        idea["generation_prompt"] = prompt[:200] + "..."
                        idea["generated_at"] = datetime.utcnow().isoformat()
                        valid_ideas.append(idea)
                
                all_ideas.extend(valid_ideas)
                logger.info(f"Batch {batch_num + 1} complete: generated {len(valid_ideas)} ideas (total: {len(all_ideas)})")
            
            logger.info(f"Successfully generated {len(all_ideas)} ideas in {num_batches} batches")
            return all_ideas
        
        except Exception as e:
            logger.error(f"Failed to generate ideas: {e}")
            raise
    
    async def refine_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine and expand an existing idea.
        
        Args:
            idea: The idea to refine
            
        Returns:
            Refined idea with additional details
        """
        prompt = f"""Refine and expand this business idea:

Title: {idea.get('title')}
Description: {idea.get('description')}

Provide:
1. Enhanced problem statement with market data
2. Detailed target audience segmentation
3. Competitive advantages and moat
4. Revenue model suggestions
5. Go-to-market strategy outline
6. Key risks and mitigation strategies

Return as JSON with these fields: enhanced_problem, audience_segments, competitive_advantages, revenue_models, gtm_strategy, risks"""
        
        try:
            refined = await self.llm.generate_json(
                prompt=prompt,
                temperature=0.7
            )
            
            # Merge with original idea
            idea.update(refined)
            return idea
        
        except Exception as e:
            logger.error(f"Failed to refine idea: {e}")
            return idea
