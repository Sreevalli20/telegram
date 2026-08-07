from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class ResearchHistory(Base):
    """ResearchHistory model for tracking research queries and results."""
    
    __tablename__ = "research_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    query_type = Column(String(50), nullable=False)  # e.g., stock_analysis, market_overview, earnings
    
    # Research results
    summary = Column(Text, nullable=True)
    data_sources = Column(Text, nullable=True)  # JSON string of sources
    confidence_score = Column(Integer, nullable=True)  # 0-100
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
