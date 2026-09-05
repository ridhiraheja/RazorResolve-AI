from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./razorresolve.db"
    SECRET_KEY: str = "razorresolve-dev-secret-key"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
