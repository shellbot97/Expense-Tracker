"""
Application configuration
Loads settings from environment variables
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./expense_tracker.db")

    # Security
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET", "dev-secret-change-in-production-min-32-chars"
    )
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    JWT_ALGORITHM: str = "HS256"

    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # AI Features (Optional)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")

    # Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Password hashing
    PASSWORD_HASH_SCHEMES: List[str] = ["bcrypt"]
    PASSWORD_HASH_DEPRECATED: str = "auto"

    # SQLite specific settings
    SQLITE_PRAGMA_FOREIGN_KEYS: bool = True
    SQLITE_PRAGMA_WAL_MODE: bool = True
    SQLITE_TIMEOUT: float = 5.0

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    @property
    def ai_enabled(self) -> bool:
        """Check if AI features are enabled"""
        return bool(self.AI_PROVIDER and self.AI_API_KEY)


# Global settings instance
settings = Settings()
