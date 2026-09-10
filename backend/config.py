"""
Application Configuration for AeroSense-AI Weather Anomaly Platform.

Defines the centralized Settings class using pydantic-settings to manage
environment variables, API prefixes, database connectivity, and CORS policies.
"""

from __future__ import annotations

from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings with environment variable support."""

    PROJECT_NAME: str = "AeroSense-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Database Configuration (SQLite default with PostgreSQL support)
    DATABASE_URL: str = "sqlite:///./weather_anomaly.db"

    # ML Model & Data Paths
    MODEL_PATH: str = "ml/models/isolation_forest.joblib"
    SCALER_PATH: str = "ml/models/scaler.joblib"
    BASELINE_STATS_PATH: str = "data/processed/baseline_statistics.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parses comma-separated string or list of origins."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]


# Global settings instance
settings = Settings()
