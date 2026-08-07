from typing import List
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Notification, db)
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()
    
    def get_pending_notifications(self) -> List[Notification]:
        """Get all notifications that haven't been sent yet."""
        return (
            self.db.query(Notification)
            .filter(Notification.is_sent == False)
            .order_by(Notification.created_at.asc())
            .all()
        )
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        related_symbol: Optional[str] = None,
        related_company: Optional[str] = None
    ) -> Notification:
        """Create a new notification."""
        return self.create(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_symbol=related_symbol,
            related_company=related_company
        )
    
    def mark_as_sent(self, notification: Notification) -> Notification:
        """Mark notification as sent."""
        from datetime import datetime
        from sqlalchemy import func
        return self.update(notification, is_sent=True, sent_at=func.now())
    
    def mark_as_read(self, notification: Notification) -> Notification:
        """Mark notification as read."""
        from datetime import datetime
        from sqlalchemy import func
        return self.update(notification, is_read=True, read_at=func.now())
