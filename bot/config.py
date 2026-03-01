import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configuration settings using Pydantic BaseSettings."""

    if os.path.exists("local.env"):
        _env_file: str = "local.env"
    elif os.path.exists("../local.env"):
        _env_file: str = "../local.env"
    else:
        _env_file: str = ".env"

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Environment Configuration
    env: str = Field(default="dev", description="Environment (local, dev, prod)")
    # PostgreSQL Configuration
    db_postgres_url: str = Field(default=os.getenv("DB_POSTGRES_URL", ""), description="PostgreSQL connection URL")
    postgres_user: str = Field(default="noti_bot", description="PostgreSQL username")
    postgres_password: str = Field(
        default="noti_bot_password", description="PostgreSQL password"
    )
    postgres_db: str = Field(
        default="noti_bot_db", description="PostgreSQL database name"
    )

    bot_client_token: str = Field(default="", description="Telegram bot client token")
    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host address")
    redis_port: int = Field(default=6379, description="Redis port number")


# Create settings instance
settings = Settings()
