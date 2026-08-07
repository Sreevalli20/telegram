from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.repositories.base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for Conversation model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Conversation, db)
    
    def get_user_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Get all conversations for a user."""
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_active_conversation(self, user_id: int) -> Optional[Conversation]:
        """Get the most recent conversation for a user."""
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .first()
        )
