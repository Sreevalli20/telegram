from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import get_db
from app.repositories import NotificationRepository, UserRepository
from app.ai.agents import NotificationAgent
from app.ai.providers import OpenAIProvider, AnthropicProvider, GoogleProvider
from app.config.settings import get_settings
import asyncio

settings = get_settings()


class NotificationScheduler:
    """Scheduler for sending notifications."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_agent = NotificationAgent(self._get_ai_provider())
    
    def _get_ai_provider(self):
        """Get the configured AI provider."""
        provider_name = settings.ai_provider.lower()
        
        if provider_name == "openai":
            return OpenAIProvider(api_key=settings.openai_api_key)
        elif provider_name == "anthropic":
            return AnthropicProvider(api_key=settings.anthropic_api_key)
        elif provider_name == "google":
            return GoogleProvider(api_key=settings.google_api_key)
        else:
            raise ValueError(f"Unknown AI provider: {provider_name}")
    
    def start(self):
        """Start the scheduler."""
        # Add daily market summary job (9 AM daily)
        self.scheduler.add_job(
            self.send_daily_market_summaries,
            CronTrigger(hour=9, minute=0),
            id="daily_market_summary",
            replace_existing=True
        )
        
        # Add notification processing job (every 5 minutes)
        self.scheduler.add_job(
            self.process_pending_notifications,
            CronTrigger(minute="*/5"),
            id="process_notifications",
            replace_existing=True
        )
        
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
    
    async def send_daily_market_summaries(self):
        """Send daily market summaries to users."""
        db = next(get_db())
        try:
            notification_repo = NotificationRepository(db)
            user_repo = UserRepository(db)
            
            # Get all active users with notifications enabled
            # This would need to be implemented with user preferences
            
            # For now, this is a placeholder
            pass
            
        finally:
            db.close()
    
    async def process_pending_notifications(self):
        """Process pending notifications."""
        db = next(get_db())
        try:
            notification_repo = NotificationRepository(db)
            
            # Get pending notifications
            pending = notification_repo.get_pending_notifications()
            
            # Process each notification
            for notification in pending:
                # Send notification via Telegram
                # This would integrate with the Telegram bot
                await self.send_telegram_notification(notification)
                
                # Mark as sent
                notification_repo.mark_as_sent(notification)
                
        finally:
            db.close()
    
    async def send_telegram_notification(self, notification):
        """Send notification via Telegram."""
        # This would integrate with the Telegram bot to send messages
        # Placeholder for now
        pass
