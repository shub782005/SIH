import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Plastic Waste Collection Optimization Platform"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "super_secret_jwt_key_for_development_mode_only_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database: SQLite fallback for local development if Postgres is not running
    DATABASE_URL: str = "sqlite:///./plastic_waste.db"
    
    OSRM_SERVER_URL: str = "http://router.project-osrm.org"
    UPLOAD_DIR: str = "uploads"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
