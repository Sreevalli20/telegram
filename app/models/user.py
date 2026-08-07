from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class User(Base):
    """User model representing Telegram bot users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # User profile
    name = Column(String(200), nullable=True)
    role = Column(String(100), nullable=True)  # e.g., investor, trader, analyst
    investment_interests = Column(Text, nullable=True)  # JSON string of interests
    preferred_sectors = Column(Text, nullable=True)  # JSON string of sectors
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
