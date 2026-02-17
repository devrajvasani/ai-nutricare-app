"""
Application settings loaded from environment variables.
All configuration is centralized here via Pydantic BaseSettings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")


class AppSettings:
    """Core application settings."""

    NAME: str = os.getenv("APP_NAME", "AI-NutriCare")
    ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    HOST: str = os.getenv("APP_HOST", "localhost")
    PORT: int = int(os.getenv("APP_PORT", 8501))


class DatabaseSettings:
    """PostgreSQL database connection settings."""

    HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("DB_PORT", 5432))
    NAME: str = os.getenv("DB_NAME", "nutricare_db")
    USER: str = os.getenv("DB_USER", "postgres")
    PASSWORD: str = os.getenv("DB_PASSWORD", "")
    POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 5))
    MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )

    @property
    def async_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}/{self.NAME}"
        )


class FileSettings:
    """File upload and storage settings."""

    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
    SAMPLE_DIR: Path = BASE_DIR / "sample_reports"
    LOG_DIR: Path = BASE_DIR / os.getenv("LOG_DIR", "logs")

    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", 20))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024

    ALLOWED_EXTENSIONS: set = set(
        os.getenv("ALLOWED_EXTENSIONS", "pdf,png,jpg,jpeg,tiff,bmp").split(",")
    )

    def __post_init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)


class OCRSettings:
    """OCR engine configuration."""

    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")
    LANGUAGE: str = os.getenv("OCR_LANGUAGE", "eng")
    ENGINE: str = os.getenv("OCR_ENGINE", "tesseract")  # tesseract | easyocr


class LogSettings:
    """Logging configuration."""

    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DIR: str = os.getenv("LOG_DIR", "logs")
    ROTATION: str = os.getenv("LOG_ROTATION", "10 MB")
    RETENTION: str = os.getenv("LOG_RETENTION", "30 days")


# ─── Singleton Instances ──────────────────────────────────────────────────────
app_settings = AppSettings()
db_settings = DatabaseSettings()
file_settings = FileSettings()
ocr_settings = OCRSettings()
log_settings = LogSettings()

# Ensure required directories exist on import
file_settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
file_settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
file_settings.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)