from typing import Optional
from sqlalchemy.orm import Session
from app.models.preference import Preference
from app.repositories.base_repository import BaseRepository


class PreferenceRepository(BaseRepository[Preference]):
    """Repository for Preference model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Preference, db)
    
    def get_user_preferences(self, user_id: int) -> Optional[Preference]:
        """Get preferences for a user."""
        return self.db.query(Preference).filter(Preference.user_id == user_id).first()
    
    def get_or_create_preferences(self, user_id: int) -> Preference:
        """Get existing preferences or create default ones."""
        prefs = self.get_user_preferences(user_id)
        if prefs:
            return prefs
        return self.create(user_id=user_id)
    
    def update_preferences(self, user_id: int, **kwargs) -> Optional[Preference]:
        """Update user preferences."""
        prefs = self.get_user_preferences(user_id)
        if prefs:
            return self.update(prefs, **kwargs)
        return self.create(user_id=user_id, **kwargs)
