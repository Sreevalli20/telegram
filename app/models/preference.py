from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class Preference(Base):
    """Preference model for user settings and customization."""
    
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Notification preferences
    enable_notifications = Column(Boolean, default=True)
    notification_frequency = Column(String(50), default="daily")  # instant, daily, weekly
    notification_types = Column(Text, nullable=True)  # JSON string of types
    
    # Content preferences
    response_style = Column(String(50), default="professional")  # professional, casual, detailed
    language = Column(String(10), default="en")
    timezone = Column(String(50), nullable=True)
    
    # Data preferences
    data_sources = Column(Text, nullable=True)  # JSON string of preferred sources
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
