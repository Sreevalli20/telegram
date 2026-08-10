from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.models import Base, engine
from app.telegram import get_bot
from app.telegram.webhook import setup_webhook, delete_webhook
from app.utils.logger import setup_logger, get_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import asyncio
import sys

settings = get_settings()
setup_logger()
logger = get_logger(__name__)


def ensure_local_directories() -> None:
    """Ensure local storage directories exist for SQLite and uploads."""
    if settings.database_url.startswith("sqlite:///"):
        file_path = Path(settings.database_url.replace("sqlite:///", ""))
        if file_path.parent and not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
    Path("uploads").mkdir(parents=True, exist_ok=True)


def validate_startup() -> bool:
    """
    Validate that all required configuration and dependencies are available.
    
    All validation is non-fatal for web service deployment. The FastAPI
    server will start even if optional integrations are unavailable.
    
    Returns:
        bool: Always True to allow FastAPI to start
    """
    logger.info("Starting application validation...")
    
    # Validate TELEGRAM_BOT_TOKEN (warn if missing, but don't fail startup)
    token = settings.telegram_bot_token
    if not token or not token.strip():
        logger.warning("TELEGRAM_BOT_TOKEN is not configured; Telegram bot will be disabled")
    else:
        logger.info("TELEGRAM_BOT_TOKEN configured: True")

    # AI provider configuration is validated when actual AI calls are made.
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY is not configured; AI requests will fail until configured")
    elif settings.ai_provider == "anthropic" and not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY is not configured; AI requests will fail until configured")
    elif settings.ai_provider == "google" and not settings.google_api_key:
        logger.warning("GOOGLE_API_KEY is not configured; AI requests will fail until configured")
    
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except SQLAlchemyError as e:
        logger.warning(f"Database connection failed: {e}. Application will start in degraded mode.")
    
    # Check webhook configuration if webhook mode is enabled
    if settings.webhook_mode and not settings.webhook_url:
        logger.warning("WEBHOOK_URL is not configured; webhook mode will not be available")
    
    logger.info("Application validation completed successfully")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("Starting ATLAS application...")

    ensure_local_directories()
    
    # Validate startup configuration (non-fatal)
    validate_startup()
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except SQLAlchemyError as e:
        logger.error(f"Failed to create database tables: {e}. Application will start in degraded mode.")
    
    # Start Telegram bot if configured
    bot = get_bot()

    if bot is None:
        logger.warning("Telegram bot is not configured; running without Telegram integration")
    else:
        # Production webhook mode - NO polling fallback
        if settings.webhook_mode:
            # Setup webhook for production
            webhook_success = await setup_webhook(bot)
            if webhook_success:
                logger.info("Webhook mode enabled - Telegram will receive updates via webhook")
            else:
                logger.error("Failed to setup webhook - Telegram bot will not receive updates")
        else:
            # Development polling mode only
            logger.info("Polling mode enabled (development only)")
            async def start_telegram_polling():
                """Start Telegram polling - development only."""
                logger.info("Starting Telegram bot initialization...")
                await bot.initialize()
                logger.info("Telegram bot initialized")
                
                logger.info("Starting Telegram bot...")
                await bot.start()
                logger.info("Telegram bot started")
                
                logger.info("Starting Telegram polling...")
                await bot.updater.start_polling()
                logger.info("Telegram polling started successfully")
            
            await start_telegram_polling()
    
    logger.info("ATLAS application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ATLAS application...")
    
    if bot is not None:
        if settings.webhook_mode:
            # Delete webhook to clean up Telegram configuration
            await delete_webhook(bot)
            logger.info("Webhook deleted during shutdown")
        else:
            # Stop polling in development mode
            try:
                await bot.updater.stop()
                await bot.stop()
                await bot.shutdown()
                logger.info("Telegram bot shutdown successfully")
            except Exception as e:
                logger.error(f"Error during Telegram bot shutdown: {e}")
    
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
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError:
        return {"status": "unhealthy", "database": "disconnected"}


@app.get("/bot/status")
async def bot_status():
    """Check bot status."""
    bot = get_bot()
    if bot is None:
        return {
            "status": "disabled",
            "mode": "none",
            "message": "Telegram bot is not configured"
        }
    
    status = {
        "status": "running" if bot.running else "stopped",
        "bot_id": bot.id,
        "mode": "webhook" if settings.webhook_mode else "polling"
    }
    
    # Add webhook information if in webhook mode
    if settings.webhook_mode:
        from app.telegram.webhook import get_webhook_info
        webhook_info = await get_webhook_info(bot)
        status["webhook"] = webhook_info
    
    return status


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram webhook updates."""
    from telegram import Update
    from json import loads
    
    bot = get_bot()
    if bot is None:
        raise HTTPException(status_code=503, detail="Telegram bot is not configured")

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
