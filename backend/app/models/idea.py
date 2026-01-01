from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
# from pgvector.sqlalchemy import Vector
import uuid

from app.database import Base


class Idea(Base):
    """Business idea model."""
    
    __tablename__ = "ideas"
    __table_args__ = (
        Index("idx_ideas_created_at", "created_at"),
        Index("idx_ideas_status", "status"),
        Index("idx_ideas_score", "overall_score"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text)
    target_audience = Column(String(500))
    value_proposition = Column(Text)
    
    # Categorization
    category = Column(String(100))
    # tags = Column(ARRAY(String), default=[])  # PG Array
    tags = Column(JSON, default=[])  # SQLite JSON
    industry = Column(String(100))
    
    # Technical details
    tech_stack = Column(JSON)
    estimated_complexity = Column(String(50))  # low, medium, high
    
    # Generation metadata
    generation_prompt = Column(Text)
    generation_params = Column(JSON)
    
    # Status tracking
    status = Column(String(50), default="generated")  # generated, researched, scored, ranked
    
    # Scoring
    overall_score = Column(Float)
    rank = Column(Integer)
    
    # Embeddings for similarity search
    # embedding = Column(Vector(384))  # PGVector
    embedding = Column(JSON)  # SQLite compatible storage for embeddings
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    researched_at = Column(DateTime)
    scored_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Idea(id={self.id}, title='{self.title[:50]}...', score={self.overall_score})>"
