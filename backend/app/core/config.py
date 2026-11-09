"""
Application configuration.

Why this exists:
    Single source of truth for runtime configuration, validated at startup.
    Fails fast if a required secret is missing — better to crash at boot
    than silently operate insecurely.

Enterprise decisions:
    - Pydantic Settings validates types at import time (no runtime surprises).
    - Secrets come from environment; never checked into git.
    - Nested `@computed_field` for derived values (e.g., DATABASE_URL).

SAP S/4HANA relevance:
    Replaces SAP's table-based configuration (SM30/SPRO) with the modern
    twelve-factor principle. In cloud deployments this map is provided by
    Kubernetes ConfigMaps + Secrets (or BTP Destination Service).
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "Procurement Automation Platform"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ---- Security ----
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:5173"

    # ---- Database ----
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # ---- Bootstrap ----
    FIRST_SUPERUSER_EMAIL: str | None = None
    FIRST_SUPERUSER_PASSWORD: str | None = None

    # ---- Logging ----
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["console", "json"] = "console"

    @field_validator("SECRET_KEY")
    @classmethod
    def _reject_placeholder_secret(cls, v: str, info) -> str:
        # In production, refuse to boot with the template placeholder.
        env = info.data.get("APP_ENV", "development")
        if env == "production" and "CHANGE_ME" in v:
            raise ValueError(
                "SECRET_KEY must be set to a real secret in production."
            )
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached accessor. `lru_cache` guarantees one Settings instance per process,
    which:
        - prevents repeated .env parsing,
        - makes dependency injection idempotent,
        - is safe under async (no shared mutable state).
    """
    return Settings()