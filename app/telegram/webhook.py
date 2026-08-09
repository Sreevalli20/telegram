"""Telegram webhook configuration and management for production deployment."""

from telegram.ext import Application
from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


async def setup_webhook(application: Application) -> bool:
    """
    Set up Telegram webhook for production deployment.
    
    Args:
        application: The Telegram Application instance
        
    Returns:
        bool: True if webhook setup was successful
    """
    if not settings.webhook_mode:
        logger.info("Webhook mode is disabled, skipping webhook setup")
        return False
    
    if not settings.webhook_url:
        logger.error("WEBHOOK_URL is not set but webhook mode is enabled")
        return False
    
    try:
        webhook_url = f"{settings.webhook_url}/telegram/webhook"
        
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=settings.webhook_secret,
            max_connections=40,
            drop_pending_updates=True
        )
        
        logger.info(f"Webhook set up successfully at {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set up webhook: {e}")
        return False


async def delete_webhook(application: Application) -> bool:
    """
    Delete Telegram webhook (useful for switching back to polling).
    
    Args:
        application: The Telegram Application instance
        
    Returns:
        bool: True if webhook deletion was successful
    """
    try:
        await application.bot.delete_webhook()
        logger.info("Webhook deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        return False


async def get_webhook_info(application: Application) -> dict:
    """
    Get current webhook information.
    
    Args:
        application: The Telegram Application instance
        
    Returns:
        dict: Webhook information
    """
    try:
        webhook_info = await application.bot.get_webhook_info()
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
        }
    except Exception as e:
        logger.error(f"Failed to get webhook info: {e}")
        return {}
