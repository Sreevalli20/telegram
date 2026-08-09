from loguru import logger
import sys
import os
from app.config.settings import get_settings

settings = get_settings()


def filter_secrets(record):
    """Filter out sensitive information from logs."""
    message = record["message"]
    
    # Filter common secret patterns
    secrets_to_filter = [
        "TELEGRAM_BOT_TOKEN",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "DATABASE_URL",
        "WEBHOOK_SECRET",
    ]
    
    for secret in secrets_to_filter:
        if secret in message:
            record["message"] = message.replace(
                message[message.find(secret):],
                f"{secret}=***REDACTED***"
            )
    
    return record


def setup_logger():
    """Configure production-ready application logger."""
    logger.remove()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Console output with colorization for development
    logger.add(
        sys.stdout,
        colorize=settings.app_env == "development",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        filter=filter_secrets
    )
    
    # File output for application logs
    logger.add(
        "logs/atlas.log",
        rotation="500 MB",
        retention="10 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        filter=filter_secrets
    )
    
    # Separate error log file
    logger.add(
        "logs/errors.log",
        rotation="100 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        filter=filter_secrets
    )
    
    return logger


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)
