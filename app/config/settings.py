from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Telegram
    telegram_bot_token: str
    
    # Database
    database_url: str = "sqlite:///./atlas.db"
    
    # AI Provider
    ai_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    max_conversation_history: int = 50
    
    # Financial APIs (Optional)
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the singleton settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
