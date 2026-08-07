from loguru import logger
import sys
from app.config.settings import get_settings

settings = get_settings()


def setup_logger():
    """Configure application logger."""
    logger.remove()
    
    # Console output
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    
    # File output
    logger.add(
        "logs/atlas.log",
        rotation="500 MB",
        retention="10 days",
        level=settings.log_level
    )
    
    return logger
