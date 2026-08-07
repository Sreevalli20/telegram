from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.models import Base, engine
from app.telegram import get_bot
import asyncio

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start Telegram bot in background
    bot = get_bot()
    bot_task = asyncio.create_task(bot.run_polling())
    
    yield
    
    # Shutdown
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


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
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/bot/status")
async def bot_status():
    """Check bot status."""
    bot = get_bot()
    return {
        "status": "running" if bot.running else "stopped",
        "bot_id": bot.id
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "development"
    )
