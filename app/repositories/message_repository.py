from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import Message, MessageRole, MessageType
from app.repositories.base_repository import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Repository for Message model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Message, db)
    
    def get_conversation_messages(
        self, 
        conversation_id: int, 
        limit: int = 50
    ) -> List[Message]:
        """Get messages for a conversation, ordered by creation time."""
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def get_conversation_history(
        self, 
        conversation_id: int, 
        limit: int = 50
    ) -> List[dict]:
        """Get conversation history as a list of dicts for AI context."""
        messages = self.get_conversation_messages(conversation_id, limit)
        return [
            {
                "role": msg.role.value,
                "content": msg.content,
                "type": msg.message_type.value
            }
            for msg in messages
        ]
    
    def create_user_message(
        self, 
        conversation_id: int, 
        content: str, 
        message_type: MessageType = MessageType.TEXT,
        file_id: Optional[str] = None
    ) -> Message:
        """Create a user message."""
        return self.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            message_type=message_type,
            content=content,
            file_id=file_id
        )
    
    def create_assistant_message(
        self, 
        conversation_id: int, 
        content: str,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> Message:
        """Create an assistant message."""
        return self.create(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            message_type=MessageType.TEXT,
            content=content,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms
        )
