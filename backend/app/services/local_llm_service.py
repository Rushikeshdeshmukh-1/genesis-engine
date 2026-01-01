"""
Local LLM Service using Ollama.
Falls back to mock data if Ollama is not available.
"""

import logging
import httpx
import json
from typing import Optional, Dict, Any
import random

logger = logging.getLogger(__name__)


class LocalLLMService:
    """Service for local LLM interactions using Ollama."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1:8b"  # Using installed model
        self.timeout = 120
        
    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> str:
        """
        Generate text using Ollama.
        Requires Ollama to be running.
        """
        # Check if Ollama is available
        if not await self.is_available():
            raise ConnectionError(
                "Ollama is not running. Please install and start Ollama:\n"
                "1. Install from https://ollama.com/download\n"
                "2. Run: ollama pull llama3.2:3b\n"
                "3. Ollama will start automatically"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }
                
                if system_prompt:
                    payload["system"] = system_prompt
                
                if json_mode:
                    payload["format"] = "json"
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    def _generate_mock_response(self, prompt: str, json_mode: bool = False) -> str:
        """Generate mock response for testing."""
        if json_mode and "business idea" in prompt.lower():
            # Mock business ideas
            mock_ideas = [
                {
                    "title": "AI-Powered Code Review Assistant",
                    "description": "An intelligent tool that analyzes code quality, suggests improvements, and detects potential bugs using machine learning.",
                    "problem_statement": "Developers spend too much time on manual code reviews",
                    "target_audience": "Software development teams and individual developers",
                    "value_proposition": "Automated, intelligent code review that saves time and improves code quality",
                    "category": "Developer Tools",
                    "tags": ["AI", "DevTools", "Code Quality"],
                    "industry": "Software Development",
                    "tech_stack": {
                        "frontend": ["React", "TypeScript"],
                        "backend": ["Python", "FastAPI"],
                        "infrastructure": ["Docker", "AWS"]
                    },
                    "estimated_complexity": "medium"
                },
                {
                    "title": "Smart Meal Planner with AI Nutrition Coach",
                    "description": "Personalized meal planning app that uses AI to create custom meal plans based on dietary preferences, health goals, and budget.",
                    "problem_statement": "People struggle to maintain healthy eating habits due to lack of time and knowledge",
                    "target_audience": "Health-conscious individuals and busy professionals",
                    "value_proposition": "Personalized nutrition guidance with automated meal planning and grocery lists",
                    "category": "HealthTech",
                    "tags": ["AI", "Health", "Nutrition"],
                    "industry": "Health & Wellness",
                    "tech_stack": {
                        "frontend": ["Next.js", "React Native"],
                        "backend": ["Node.js", "PostgreSQL"],
                        "infrastructure": ["Firebase", "Google Cloud"]
                    },
                    "estimated_complexity": "medium"
                },
                {
                    "title": "Remote Team Collaboration Hub",
                    "description": "All-in-one platform for remote teams with integrated video calls, project management, and async communication tools.",
                    "problem_statement": "Remote teams use too many disconnected tools for collaboration",
                    "target_audience": "Remote-first companies and distributed teams",
                    "value_proposition": "Single platform that replaces 5+ tools with seamless integration",
                    "category": "SaaS",
                    "tags": ["Remote Work", "Collaboration", "Productivity"],
                    "industry": "Business Software",
                    "tech_stack": {
                        "frontend": ["Vue.js", "Electron"],
                        "backend": ["Go", "Redis"],
                        "infrastructure": ["Kubernetes", "AWS"]
                    },
                    "estimated_complexity": "high"
                },
                {
                    "title": "Sustainable Fashion Marketplace",
                    "description": "Platform connecting eco-conscious consumers with sustainable fashion brands, featuring carbon footprint tracking.",
                    "problem_statement": "Consumers want sustainable fashion but struggle to find verified eco-friendly brands",
                    "target_audience": "Environmentally conscious fashion shoppers",
                    "value_proposition": "Curated marketplace of verified sustainable brands with transparency on environmental impact",
                    "category": "E-commerce",
                    "tags": ["Sustainability", "Fashion", "Marketplace"],
                    "industry": "Retail",
                    "tech_stack": {
                        "frontend": ["React", "Next.js"],
                        "backend": ["Python", "Django"],
                        "infrastructure": ["Stripe", "AWS"]
                    },
                    "estimated_complexity": "medium"
                },
                {
                    "title": "Local Service Booking Platform",
                    "description": "Mobile-first platform for booking local services (plumbers, electricians, cleaners) with instant pricing and availability.",
                    "problem_statement": "Finding and booking reliable local service providers is time-consuming and uncertain",
                    "target_audience": "Homeowners and renters needing local services",
                    "value_proposition": "Instant booking with verified professionals, transparent pricing, and quality guarantees",
                    "category": "Marketplace",
                    "tags": ["Local Services", "On-Demand", "Mobile"],
                    "industry": "Home Services",
                    "tech_stack": {
                        "frontend": ["React Native", "Flutter"],
                        "backend": ["Node.js", "MongoDB"],
                        "infrastructure": ["Twilio", "Google Maps API"]
                    },
                    "estimated_complexity": "high"
                }
            ]
            
            # Return random subset
            count = min(5, len(mock_ideas))
            selected = random.sample(mock_ideas, count)
            return json.dumps(selected)
        
        return "Mock response: Ollama is not running. Please install and start Ollama to use local LLMs."


# Global instance
local_llm_service = LocalLLMService()
