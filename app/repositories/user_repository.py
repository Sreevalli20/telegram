from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_or_create_by_telegram_id(self, telegram_id: int, **kwargs) -> User:
        """Get existing user or create new one."""
        user = self.get_by_telegram_id(telegram_id)
        if user:
            return user
        return self.create(telegram_id=telegram_id, **kwargs)
    
    def update_last_interaction(self, user: User) -> User:
        """Update user's last interaction timestamp."""
        from datetime import datetime
        from sqlalchemy import func
        return self.update(user, last_interaction_at=func.now())
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return self.db.query(User).filter(User.is_active == True).all()
