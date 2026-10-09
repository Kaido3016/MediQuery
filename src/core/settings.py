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
    storage_backend: str = "local"
    object_storage_bucket: str | None = None
    object_storage_region: str = "ca-central-1"
    object_storage_endpoint_url: str | None = None
    object_storage_kms_key_id: str | None = None
    clamav_host: str | None = None
    clamav_port: int = Field(default=3310, ge=1, le=65535)
    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    frontend_base_url: str = "http://localhost:8501"
    email_token_minutes: int = Field(default=30, ge=5, le=1440)
    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None
    stripe_price_id: str | None = None
    stripe_success_url: str | None = None
    stripe_cancel_url: str | None = None
    mfa_issuer: str = "MediQuery"

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
            if self.storage_backend != "s3":
                raise RuntimeError("Production requires private S3-compatible object storage")
            if not self.object_storage_bucket or not self.object_storage_kms_key_id:
                raise RuntimeError("Production object storage bucket and KMS key are required")
            if not self.clamav_host:
                raise RuntimeError("Production requires a configured malware-scanning service")
            if not all((self.smtp_host, self.smtp_from_email)):
                raise RuntimeError("Production requires SMTP delivery for account security emails")
            if not all((self.stripe_secret_key, self.stripe_webhook_secret, self.stripe_price_id,
                        self.stripe_success_url, self.stripe_cancel_url)):
                raise RuntimeError("Production billing requires complete Stripe configuration")
            if not self.rate_limit_redis_url:
                raise RuntimeError(
                    "RATE_LIMIT_REDIS_URL is required in production for shared rate limiting"
                )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_for_runtime()
    return settings
