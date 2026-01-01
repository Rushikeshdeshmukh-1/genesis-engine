"""
Test configuration and fixtures.
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_idea():
    """Sample idea for testing."""
    return {
        "title": "AI-Powered Code Review Tool",
        "description": "Automated code review using machine learning",
        "category": "Developer Tools",
        "tags": ["AI", "DevTools", "Automation"],
        "problem_statement": "Manual code reviews are time-consuming",
        "target_audience": "Software development teams",
        "value_proposition": "Save 50% of code review time",
    }


@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    return {
        "competitors": [
            {
                "name": "CodeClimate",
                "url": "https://codeclimate.com",
                "market_position": "leader"
            }
        ],
        "market_size": "$5B TAM",
        "trends": ["AI adoption", "DevOps automation"]
    }
