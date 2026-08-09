from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.models import Base, engine
from app.telegram import get_bot
from app.telegram.webhook import setup_webhook, delete_webhook
from app.utils.logger import setup_logger, get_logger
from sqlalchemy.exc import SQLAlchemyError
import asyncio
import sys

settings = get_settings()
setup_logger()
logger = get_logger(__name__)


def validate_startup() -> bool:
    """
    Validate that all required configuration and dependencies are available.
    
    Returns:
        bool: True if validation passes
    """
    logger.info("Starting application validation...")
    
    # Check required environment variables
    required_vars = {
        "TELEGRAM_BOT_TOKEN": settings.telegram_bot_token,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    # Check AI provider configuration
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        logger.error("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'")
        return False
    elif settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY is required when AI_PROVIDER is 'anthropic'")
        return False
    elif settings.ai_provider == "google" and not settings.google_api_key:
        logger.error("GOOGLE_API_KEY is required when AI_PROVIDER is 'google'")
        return False
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False
    
    # Check webhook configuration if webhook mode is enabled
    if settings.webhook_mode and not settings.webhook_url:
        logger.error("WEBHOOK_URL is required when WEBHOOK_MODE is enabled")
        return False
    
    logger.info("Application validation completed successfully")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting ATLAS application...")
    
    # Validate startup configuration
    if not validate_startup():
        logger.error("Startup validation failed. Exiting...")
        sys.exit(1)
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}")
        sys.exit(1)
    
    # Start Telegram bot
    bot = get_bot()
    bot_task = None
    
    if settings.webhook_mode:
        # Setup webhook for production
        webhook_success = await setup_webhook(bot)
        if webhook_success:
            logger.info("Webhook mode enabled")
        else:
            logger.warning("Failed to setup webhook, falling back to polling")
            bot_task = asyncio.create_task(bot.run_polling())
    else:
        # Use polling for development
        logger.info("Polling mode enabled")
        bot_task = asyncio.create_task(bot.run_polling())
    
    logger.info("ATLAS application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ATLAS application...")
    
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    
    if settings.webhook_mode:
        await delete_webhook(bot)
    
    logger.info("ATLAS application shutdown complete")


app = FastAPI(
    title="ATLAS - AI Financial Assistant",
    description="AI-powered Financial Assistant for Telegram",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ATLAS - AI Financial Assistant",
        "status": "running",
        "version": "1.0.0",
        "mode": "webhook" if settings.webhook_mode else "polling"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError:
        return {"status": "unhealthy", "database": "disconnected"}


@app.get("/bot/status")
async def bot_status():
    """Check bot status."""
    bot = get_bot()
    return {
        "status": "running" if bot.running else "stopped",
        "bot_id": bot.id,
        "mode": "webhook" if settings.webhook_mode else "polling"
    }


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates."""
    from telegram import Update
    from json import loads
    
    bot = get_bot()
    
    # Verify webhook secret if configured
    if settings.webhook_secret:
        secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret != settings.webhook_secret:
            logger.warning("Invalid webhook secret")
            raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Process update
    body = await request.body()
    update = Update.de_json(loads(body), bot.bot)
    
    await bot.process_update(update)
    
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.app_env == "development"
    )
