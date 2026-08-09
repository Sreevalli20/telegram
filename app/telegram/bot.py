from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from app.config.settings import get_settings
from app.telegram.handlers import get_handlers, button_callback
from app.telegram.middleware import error_handler
from app.utils.logger import get_logger
import os
import sys

logger = get_logger(__name__)

# Module-level diagnostic
logger.info(f"app.telegram.bot module loaded, Python version: {sys.version}")


def create_bot(token: str):
    """Create and configure the Telegram bot application.
    
    Args:
        token: The Telegram bot token
        
    Returns:
        The configured Telegram Application instance or None if creation fails
    """
    logger.info("create_bot() called with token")
    
    # Use stripped token
    token = token.strip()
    
    try:
        logger.info("Building Telegram Application...")
        application = Application.builder().token(token).build()
        logger.info("Telegram Application built successfully")
        
        # Add handlers
        logger.info("Getting handlers...")
        handlers = get_handlers()
        logger.info(f"Got {len(handlers)} handlers")
        
        for handler in handlers:
            application.add_handler(handler)
        logger.info("Handlers added successfully")
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(button_callback))
        logger.info("Callback query handler added")
        
        # Add error handler
        application.add_error_handler(error_handler)
        logger.info("Error handler added")
        
        logger.info("create_bot() returning application successfully")
        return application
    except Exception as e:
        logger.error(f"Failed to create Telegram bot: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


_bot_instance = None


def get_bot():
    """Get the singleton bot instance."""
    global _bot_instance
    logger.info(f"get_bot() called, _bot_instance is None: {_bot_instance is None}")
    
    if _bot_instance is None:
        logger.info("Telegram bot initialization attempted")
        
        # Direct environment read to avoid any Pydantic issues
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        logger.info(f"Token from os.environ: present={token is not None}, empty={not token or not token.strip()}")
        
        if not token or not token.strip():
            logger.warning("TELEGRAM_BOT_TOKEN is not configured; bot will remain disabled")
            return None
        
        logger.info("Token found, proceeding with bot creation")
        _bot_instance = create_bot(token)
        
        if _bot_instance is not None:
            logger.info("Telegram bot initialized successfully")
        else:
            logger.error("Telegram bot initialization failed: create_bot() returned None")
    else:
        logger.info("Returning existing bot instance")
    
    logger.info(f"get_bot() returning: {_bot_instance is not None}")
    return _bot_instance
