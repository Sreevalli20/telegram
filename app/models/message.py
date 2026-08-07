from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.models import Base


class MessageType(enum.Enum):
    """Types of messages in the conversation."""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    PDF = "pdf"
    SYSTEM = "system"


class MessageRole(enum.Enum):
    """Roles in the conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base):
    """Message model representing individual messages in conversations."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(Text, nullable=True)
    
    # For file uploads
    file_id = Column(String(200), nullable=True)
    file_path = Column(String(500), nullable=True)
    
    # AI processing metadata
    tokens_used = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
