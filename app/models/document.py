from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base


class Document(Base):
    """Document model for uploaded files (PDF, images)."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    # File information
    file_id = Column(BigInteger, nullable=True)  # Telegram file ID
    file_type = Column(String(50), nullable=False)  # pdf, image
    file_name = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Processing metadata
    extracted_text = Column(Text, nullable=True)
    analysis_summary = Column(Text, nullable=True)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation")
