"""
Simple mock API server for testing the frontend.
Run this to test the frontend without the full backend infrastructure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
mock_ideas = [
    {
        "id": "1",
        "title": "AI-Powered Code Review Assistant",
        "description": "Automated code review tool using machine learning to detect bugs, security issues, and suggest improvements",
        "category": "Developer Tools",
        "tags": ["AI", "DevTools", "Automation"],
        "status": "ranked",
        "overall_score": 87.5,
        "rank": 1,
        "created_at": "2025-12-07T10:00:00Z"
    },
    {
        "id": "2",
        "title": "Smart Home Energy Optimizer",
        "description": "IoT platform that learns usage patterns and automatically optimizes energy consumption",
        "category": "IoT",
        "tags": ["IoT", "Energy", "Sustainability"],
        "status": "scored",
        "overall_score": 82.3,
        "rank": 2,
        "created_at": "2025-12-07T10:05:00Z"
    },
    {
        "id": "3",
        "title": "Virtual Health Coach Platform",
        "description": "AI-driven personalized health and fitness coaching with real-time monitoring",
        "category": "HealthTech",
        "tags": ["AI", "Health", "Fitness"],
        "status": "scored",
        "overall_score": 79.8,
        "rank": 3,
        "created_at": "2025-12-07T10:10:00Z"
    },
    {
        "id": "4",
        "title": "Blockchain Supply Chain Tracker",
        "description": "Transparent supply chain management using blockchain technology",
        "category": "Blockchain",
        "tags": ["Blockchain", "Supply Chain", "Transparency"],
        "status": "researched",
        "overall_score": 75.2,
        "rank": 4,
        "created_at": "2025-12-07T10:15:00Z"
    },
    {
        "id": "5",
        "title": "AR Shopping Experience",
        "description": "Augmented reality platform for virtual try-before-you-buy shopping",
        "category": "E-commerce",
        "tags": ["AR", "E-commerce", "Retail"],
        "status": "researched",
        "overall_score": 71.5,
        "rank": 5,
        "created_at": "2025-12-07T10:20:00Z"
    }
]

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "Mock API Server", "version": "1.0.0"}

@app.get("/api/v1/ideas/stats/summary")
async def get_stats():
    return {
        "total_ideas": len(mock_ideas),
        "average_score": sum(i["overall_score"] for i in mock_ideas) / len(mock_ideas),
        "by_status": {
            "generated": 0,
            "researched": 2,
            "scored": 3,
            "ranked": 5
        }
    }

@app.get("/api/v1/ideas/")
async def get_ideas():
    return {
        "ideas": mock_ideas,
        "total": len(mock_ideas),
        "page": 1,
        "page_size": 20
    }

@app.get("/api/v1/ideas/{idea_id}")
async def get_idea(idea_id: str):
    idea = next((i for i in mock_ideas if i["id"] == idea_id), None)
    if idea:
        return {
            **idea,
            "problem_statement": "Current solutions are inefficient and expensive",
            "target_audience": "Small to medium businesses",
            "value_proposition": "Save 50% of time and costs"
        }
    return {"error": "Not found"}

@app.get("/api/v1/scoring/{idea_id}")
async def get_score(idea_id: str):
    return {
        "overall_score": 87.5,
        "normalized_score": 87.5,
        "percentile_rank": 95,
        "confidence_score": 85,
        "market_demand_score": 90,
        "competition_score": 75,
        "trend_strength_score": 88,
        "revenue_potential_score": 92,
        "tech_feasibility_score": 85,
        "cost_to_build_score": 70,
        "risk_level_score": 65,
        "user_adoption_score": 88,
        "scalability_score": 90,
        "innovation_score": 95,
        "moat_strength_score": 80,
        "operational_complexity_score": 75,
        "time_to_market_score": 85,
        "team_requirements_score": 78,
        "social_impact_score": 70,
        "global_expansion_score": 85
    }

@app.get("/api/v1/research/{idea_id}")
async def get_research(idea_id: str):
    return [
        {
            "id": "1",
            "title": "Market Analysis",
            "research_type": "market",
            "summary": "The market is growing at 25% CAGR with strong demand",
            "confidence_score": 85
        },
        {
            "id": "2",
            "title": "Technology Trends",
            "research_type": "trend",
            "summary": "AI and automation are key trends driving adoption",
            "confidence_score": 90
        }
    ]

@app.get("/api/v1/research/{idea_id}/competitors")
async def get_competitors(idea_id: str):
    return [
        {
            "id": "1",
            "name": "CompetitorA",
            "url": "https://competitora.com",
            "description": "Leading player in the market",
            "market_position": "leader",
            "strengths": ["Strong brand", "Large user base"],
            "weaknesses": ["High pricing", "Complex UI"]
        },
        {
            "id": "2",
            "name": "CompetitorB",
            "url": "https://competitorb.com",
            "description": "Fast-growing startup",
            "market_position": "challenger",
            "strengths": ["Innovative features", "Good UX"],
            "weaknesses": ["Limited market presence", "Funding constraints"]
        }
    ]

@app.get("/api/v1/research/{idea_id}/market")
async def get_market(idea_id: str):
    return {
        "tam": "$5.2B",
        "sam": "$1.8B",
        "som": "$180M",
        "growth_rate": "25% CAGR",
        "trends": ["AI adoption increasing", "Remote work driving demand", "Cloud migration"],
        "drivers": ["Cost reduction", "Efficiency gains", "Competitive pressure"]
    }

@app.post("/api/v1/ideas/generate")
async def generate_ideas(request: dict):
    return {
        "message": "Ideas generated successfully",
        "count": request.get("count", 10),
        "ideas": mock_ideas[:request.get("count", 10)]
    }

if __name__ == "__main__":
    print("🚀 Starting Mock API Server on http://localhost:8000")
    print("📊 Frontend should be running on http://localhost:3000")
    print("✅ CORS enabled for localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
