from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, Union
import os


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    
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
    
    # Webhook Configuration
    webhook_mode: bool = False
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Financial APIs (Optional)
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    
    # Security Configuration
    max_file_size_mb: int = 20
    allowed_file_types: str = "pdf,png,jpg,jpeg"
    rate_limit_per_minute: int = 30
    
    @field_validator('webhook_mode', mode='before')
    @classmethod
    def parse_webhook_mode(cls, v: Union[bool, str]) -> bool:
        """Parse webhook_mode from string or bool."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Configure database path for Render production environment
        if os.environ.get("RENDER") == "true":
            # Use Render's persistent storage directory
            data_dir = "/opt/render/project/data"
            os.makedirs(data_dir, exist_ok=True)
            self.database_url = f"sqlite:///{data_dir}/atlas.db"


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the singleton settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
