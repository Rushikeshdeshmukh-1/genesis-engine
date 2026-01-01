from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ResearchArtifact(Base):
    """Research artifacts and findings for ideas."""
    
    __tablename__ = "research_artifacts"
    __table_args__ = (
        Index("idx_research_idea_id", "idea_id"),
        Index("idx_research_type", "research_type"),
        Index("idx_research_created_at", "created_at"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    
    # Research type
    research_type = Column(String(100), nullable=False)  # competitor, market, trend, tech, legal
    
    # Research data
    title = Column(String(500))
    summary = Column(Text)
    findings = Column(JSON)  # Structured findings
    raw_data = Column(JSON)  # Raw scraped/API data
    
    # Source information
    sources = Column(JSON)  # List of URLs and references
    confidence_score = Column(Integer)  # 0-100
    
    # Storage references
    artifact_url = Column(String(1000))  # MinIO URL for stored artifacts
    screenshots = Column(JSON)  # List of screenshot URLs
    
    # Metadata
    research_duration_seconds = Column(Integer)
    tokens_used = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ResearchArtifact(id={self.id}, type='{self.research_type}', idea_id={self.idea_id})>"


class CompetitorAnalysis(Base):
    """Detailed competitor analysis."""
    
    __tablename__ = "competitor_analysis"
    __table_args__ = (
        Index("idx_competitor_idea_id", "idea_id"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    
    # Competitor details
    competitor_name = Column(String(200), nullable=False)
    competitor_url = Column(String(1000))
    description = Column(Text)
    
    # Analysis
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    market_position = Column(String(100))  # leader, challenger, niche
    estimated_revenue = Column(String(100))
    funding_info = Column(JSON)
    
    # Differentiation
    differentiation_opportunities = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CompetitorAnalysis(id={self.id}, competitor='{self.competitor_name}')>"


class MarketResearch(Base):
    """Market sizing and opportunity research."""
    
    __tablename__ = "market_research"
    __table_args__ = (
        Index("idx_market_idea_id", "idea_id"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    
    # Market sizing
    total_addressable_market = Column(String(200))
    serviceable_addressable_market = Column(String(200))
    serviceable_obtainable_market = Column(String(200))
    
    # Market dynamics
    market_growth_rate = Column(String(100))
    market_trends = Column(JSON)
    market_drivers = Column(JSON)
    market_barriers = Column(JSON)
    
    # Customer insights
    target_segments = Column(JSON)
    customer_pain_points = Column(JSON)
    willingness_to_pay = Column(String(200))
    
    # Sources and confidence
    data_sources = Column(JSON)
    confidence_level = Column(String(50))  # high, medium, low
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<MarketResearch(id={self.id}, idea_id={self.idea_id})>"
