"""Telegram middleware for error handling and security."""

from telegram import Update
from telegram.ext import ContextTypes
from app.utils.logger import get_logger
from app.config.settings import get_settings
import time
from typing import Callable, Awaitable

logger = get_logger(__name__)
settings = get_settings()


class RateLimiter:
    """Simple in-memory rate limiter for user requests."""
    
    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limit."""
        current_time = time.time()
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Remove old requests outside the window
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if current_time - req_time < self.window_seconds
        ]
        
        if len(self.user_requests[user_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        self.user_requests[user_id].append(current_time)
        return True


rate_limiter = RateLimiter(max_requests=settings.rate_limit_per_minute)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors from Telegram updates.
    
    Args:
        update: The Telegram update
        context: The context object
    """
    logger.error(f"Error while processing update {update}: {context.error}")
    
    # Try to inform user about the error
    if update and update.message:
        try:
            if context.error:
                error_message = "⚠️ An error occurred while processing your request. Please try again."
                await update.message.reply_text(error_message)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


async def rate_limit_middleware(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
) -> None:
    """
    Middleware to check rate limits before processing updates.
    
    Args:
        update: The Telegram update
        context: The context object
        handler: The handler function to call if rate limit is not exceeded
    """
    if update and update.effective_user:
        user_id = update.effective_user.id
        
        if not rate_limiter.is_allowed(user_id):
            if update.message:
                await update.message.reply_text(
                    "⚠️ You're sending messages too quickly. Please wait a moment before trying again."
                )
            return
    
    await handler(update, context)


async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log incoming updates for debugging and monitoring.
    
    Args:
        update: The Telegram update
        context: The context object
    """
    if update:
        user_id = update.effective_user.id if update.effective_user else None
        chat_id = update.effective_chat.id if update.effective_chat else None
        
        if update.message:
            message_type = update.message.content_type
            logger.info(f"Received {message_type} from user {user_id} in chat {chat_id}")
        elif update.callback_query:
            logger.info(f"Received callback query from user {user_id} in chat {chat_id}")
