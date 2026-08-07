from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class CompanyWatchlist(Base):
    """CompanyWatchlist model for tracking companies users follow."""
    
    __tablename__ = "company_watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    company_name = Column(String(200), nullable=True)
    
    # Watchlist metadata
    notes = Column(String(500), nullable=True)
    alert_price_above = Column(Float, nullable=True)
    alert_price_below = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
