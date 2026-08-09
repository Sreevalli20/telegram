from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from app.config.settings import get_settings
from app.telegram.handlers import get_handlers, button_callback
from app.telegram.middleware import error_handler
from app.utils.logger import get_logger
import os

logger = get_logger(__name__)


def create_bot(token: str):
    """Create and configure the Telegram bot application.
    
    Args:
        token: The Telegram bot token
        
    Returns:
        The configured Telegram Application instance or None if creation fails
    """
    # Use stripped token
    token = token.strip()
    
    try:
        application = Application.builder().token(token).build()
        
        # Add handlers
        handlers = get_handlers()
        for handler in handlers:
            application.add_handler(handler)
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        return application
    except Exception as e:
        logger.error(f"Failed to create Telegram bot: {e}")
        return None


_bot_instance = None


def get_bot():
    """Get the singleton bot instance."""
    global _bot_instance
    if _bot_instance is None:
        logger.info("Telegram bot initialization attempted")
        
        # Direct environment read to avoid any Pydantic issues
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        
        if not token or not token.strip():
            logger.warning("TELEGRAM_BOT_TOKEN is not configured; bot will remain disabled")
            return None
        
        logger.info("Token found, proceeding with bot creation")
        _bot_instance = create_bot(token)
        
        if _bot_instance is not None:
            logger.info("Telegram bot initialized successfully")
        else:
            logger.error("Telegram bot initialization failed: create_bot() returned None")
    return _bot_instance
