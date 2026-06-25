"""Application configuration loaded from the environment.

All settings are sourced from environment variables (or a local ``.env`` file)
and exposed through a single typed :class:`Settings` object. Importing
configuration anywhere else in the codebase goes through :func:`get_settings`
so the values are parsed and validated exactly once.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["local", "production", "test"]

_INSECURE_SECRETS = {"change-me-in-production", "", "secret", "changeme"}


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from environment variables; unknown variables are ignored
    so the same process can coexist with unrelated environment configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Runtime -----------------------------------------------------------
    environment: Environment = Field(default="local", alias="CAREERFLOW_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    project_name: str = Field(default="CareerFlow", alias="PROJECT_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # --- Database ----------------------------------------------------------
    database_url: str = Field(
        default="postgresql+psycopg://careerflow:careerflow@localhost:5432/careerflow",
        alias="DATABASE_URL",
    )

    # --- Security ----------------------------------------------------------
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_minutes: int = Field(
        default=60 * 24 * 7, alias="REFRESH_TOKEN_EXPIRE_MINUTES"
    )
    bcrypt_rounds: int = Field(default=12, ge=4, le=18, alias="BCRYPT_ROUNDS")

    # --- CORS --------------------------------------------------------------
    # ``NoDecode`` stops pydantic-settings from JSON-decoding the env value so
    # the validator below can accept a plain comma-separated string. Defaults
    # cover the Vite dev server plus the Capacitor wrapper's WebView origins
    # (https://localhost on Android, capacitor://localhost on iOS) so the
    # mobile app talks to a local backend out of the box.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://localhost",
            "http://localhost",
            "capacitor://localhost",
            "ionic://localhost",
        ],
        alias="CORS_ORIGINS",
    )

    # --- Observability -----------------------------------------------------
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    # --- AI (CV tailoring) -------------------------------------------------
    # When an OpenAI key is set, CV tailoring uses the model below. Without a
    # key the app falls back to a deterministic stub so the feature works
    # end-to-end in development and tests without external calls or cost.
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    @property
    def ai_enabled(self) -> bool:
        """True when a real AI provider (OpenAI) is configured."""
        return bool(self.openai_api_key)

    # --- Uploads -----------------------------------------------------------
    upload_dir: str = Field(default="var/uploads", alias="UPLOAD_DIR")
    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024, alias="MAX_UPLOAD_SIZE_BYTES")

    # --- Object storage (S3-compatible, e.g. Cloudflare R2) ----------------
    # When a bucket + credentials are configured, document uploads go to S3/R2
    # instead of the local disk (which is ephemeral on managed hosts). Leave
    # blank for local development.
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_access_key_id: str | None = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    s3_region: str = Field(default="auto", alias="S3_REGION")

    @property
    def s3_configured(self) -> bool:
        return bool(self.s3_bucket and self.s3_access_key_id and self.s3_secret_access_key)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Allow a comma-separated string for CORS origins in env files."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: object) -> object:
        """Pin SQLAlchemy to the psycopg (v3) driver we actually ship.

        Managed Postgres providers (Render, Heroku, Supabase, etc.) hand out
        DSNs with the bare ``postgresql://`` scheme. SQLAlchemy then tries to
        load its default Postgres dialect, which is ``psycopg2`` — a module
        that is *not* installed in our image. The result is a startup crash
        with ``ModuleNotFoundError: No module named 'psycopg2'``.

        Rewriting the scheme to ``postgresql+psycopg`` is the official
        SQLAlchemy 2.0 way to select the v3 driver; it is a no-op when the
        URL already names a driver.
        """
        if isinstance(value, str):
            if value.startswith("postgres://"):
                # Heroku-style legacy scheme.
                value = "postgresql://" + value[len("postgres://") :]
            if value.startswith("postgresql://"):
                return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate_for_runtime(self) -> None:
        """Fail fast on insecure configuration outside local/test profiles."""
        if self.is_production and self.jwt_secret in _INSECURE_SECRETS:
            raise RuntimeError("JWT_SECRET must be set to a strong, unique value in production.")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (parsed once, then cached)."""
    return Settings()
