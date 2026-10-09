"""Typed, server-only runtime configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a local `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    database_url: str = "sqlite:///./mediquery.db"
    jwt_secret: str = "development-only-change-me-before-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=30, ge=5, le=1440)
    cors_origins: list[str] = ["http://localhost:8501", "http://localhost:3000"]
    upload_root: Path = Path("private_uploads")
    max_report_bytes: int = Field(
        default=10 * 1024 * 1024, ge=1024, le=50 * 1024 * 1024
    )
    max_pdf_pages: int = Field(default=100, ge=1, le=500)
    free_report_limit: int = Field(default=3, ge=0)
    billing_checkout_url: str | None = None
    metrics_token: str | None = None
    rate_limit_redis_url: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def validate_for_runtime(self) -> None:
        """Fail closed for settings that must not reach a production environment."""
        if self.environment.lower() == "production":
            if (
                self.jwt_secret == "development-only-change-me-before-production"
                or len(self.jwt_secret) < 32
            ):
                raise RuntimeError(
                    "JWT_SECRET must be a unique value of at least 32 characters in production"
                )
            if self.database_url.startswith("sqlite"):
                raise RuntimeError(
                    "Production requires a managed database; SQLite is development-only"
                )
            if any(origin.startswith("http://") for origin in self.cors_origins):
                raise RuntimeError("Production CORS origins must use HTTPS")
            if self.metrics_token is not None and len(self.metrics_token) < 32:
                raise RuntimeError(
                    "METRICS_TOKEN must be at least 32 characters when configured"
                )
            if not self.rate_limit_redis_url:
                raise RuntimeError(
                    "RATE_LIMIT_REDIS_URL is required in production for shared rate limiting"
                )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_for_runtime()
    return settings
