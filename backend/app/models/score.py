from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base


class IdeaScore(Base):
    """Comprehensive scoring results for ideas."""
    
    __tablename__ = "idea_scores"
    __table_args__ = (
        Index("idx_scores_idea_id", "idea_id"),
        Index("idx_scores_overall", "overall_score"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Overall scoring
    overall_score = Column(Float, nullable=False)  # Weighted aggregate
    normalized_score = Column(Float)  # 0-100 scale
    percentile_rank = Column(Float)  # Compared to all ideas
    
    # Category scores (16 main categories)
    market_demand_score = Column(Float)
    competition_score = Column(Float)
    trend_strength_score = Column(Float)
    revenue_potential_score = Column(Float)
    tech_feasibility_score = Column(Float)
    cost_to_build_score = Column(Float)
    risk_level_score = Column(Float)
    user_adoption_score = Column(Float)
    scalability_score = Column(Float)
    innovation_score = Column(Float)
    moat_strength_score = Column(Float)
    operational_complexity_score = Column(Float)
    time_to_market_score = Column(Float)
    team_requirements_score = Column(Float)
    social_impact_score = Column(Float)
    global_expansion_score = Column(Float)
    
    # Detailed factor breakdown (stored as JSON)
    factor_scores = Column(JSON)  # All 1000+ individual factor scores
    
    # Scoring metadata
    scoring_model = Column(String(100))
    scoring_version = Column(String(50))
    confidence_score = Column(Float)  # Model's confidence in scoring
    
    # Performance metrics
    scoring_duration_seconds = Column(Integer)
    tokens_used = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<IdeaScore(id={self.id}, idea_id={self.idea_id}, score={self.overall_score:.2f})>"


class ScoringFactor(Base):
    """Individual scoring factor definitions (loaded from config)."""
    
    __tablename__ = "scoring_factors"
    __table_args__ = (
        Index("idx_factors_category", "category"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Factor identification
    factor_code = Column(String(100), unique=True, nullable=False)
    factor_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100))
    
    # Factor details
    description = Column(Text)
    evaluation_criteria = Column(Text)
    
    # Weighting
    weight = Column(Float, default=1.0)
    is_active = Column(Integer, default=1)
    
    # Scoring guidance
    scoring_prompt = Column(Text)
    min_score = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ScoringFactor(code='{self.factor_code}', category='{self.category}')>"
