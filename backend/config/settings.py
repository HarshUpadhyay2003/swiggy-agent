"""
Swiggy AI Copilot — Production Configuration Centralization
Provides immutable settings and dynamic environment configurations for RC-1 release.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Settings:
    # Application Metadata
    APP_NAME: str = "Swiggy AI Copilot"
    VERSION: str = "1.0.0"
    RELEASE: str = "RC-1"
    ARCHITECTURE_VERSION: str = "Stage2C"
    RANKING_VERSION: str = "Stage4D"
    SEMANTIC_VERSION: str = "Stage4F1"
    BUILD_DATE: str = "2026-07"
    API_PREFIX: str = ""

    # Environment & Server Config
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    PORT: int = int(os.getenv("PORT", 8000))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:3000",
        "https://swiggy-agent.vercel.app",
    ]
    CORS_REGEX: str = r"https://.*\.vercel\.app"

    # AI / LLM Integration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


settings = Settings()
