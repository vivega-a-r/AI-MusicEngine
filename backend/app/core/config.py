import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "IncuBrix Music Studio"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # Audio Engineering Constraints
    SAMPLE_RATE: int = 48000
    TARGET_LUFS: float = -16.0
    MAX_TRUE_PEAK_DBTP: float = -1.0
    MIN_DURATION_S: float = 5.0
    MAX_DURATION_S: float = 300.0
    DURATION_TOLERANCE_S: float = 0.05
    
    # Storage & Persistence
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", str(Path(__file__).resolve().parents[3] / "storage" / "audio"))
    DB_PATH: str = os.getenv("DB_PATH", str(Path(__file__).resolve().parents[3] / "storage" / "jobs.db"))
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "incubrix-super-secret-key-change-in-production-2026")
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID", None)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = os.getenv("FIREBASE_CREDENTIALS_PATH", None)
    ENABLE_LOCAL_DEV_AUTH: bool = os.getenv("ENABLE_LOCAL_DEV_AUTH", "true").lower() == "true"
    
    # Task Queue & Concurrency
    MAX_WORKER_CONCURRENCY: int = int(os.getenv("MAX_WORKER_CONCURRENCY", "4"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
