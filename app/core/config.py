from __future__ import annotations
from pydantic import EmailStr
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "TaskTracker"
    environment: str = "development"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Other
    debug: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()