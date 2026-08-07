from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from app.config.settings import get_settings
from app.telegram.handlers import get_handlers, button_callback

settings = get_settings()


def create_bot():
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add handlers
    handlers = get_handlers()
    for handler in handlers:
        application.add_handler(handler)
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    return application


_bot_instance = None


def get_bot():
    """Get the singleton bot instance."""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = create_bot()
    return _bot_instance
