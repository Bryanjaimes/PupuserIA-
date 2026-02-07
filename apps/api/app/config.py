"""
Application configuration via environment variables.
Uses pydantic-settings for type-safe config management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──
    app_name: str = "Gateway El Salvador API"
    debug: bool = False
    environment: str = "development"

    # ── Database ──
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway_es"
    database_pool_size: int = 20

    # ── Redis ──
    redis_url: str = "redis://localhost:6379"

    # ── AI — Anthropic ──
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # ── AI — Vector DB ──
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index: str = "gateway-es-knowledge"

    # ── Payments — Stripe ──
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # ── Meilisearch ──
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = ""

    # ── CORS ──
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # ── JWT / Auth ──
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30

    # ── AWS ──
    aws_region: str = "us-east-1"
    s3_bucket: str = "gateway-es-assets"


settings = Settings()
