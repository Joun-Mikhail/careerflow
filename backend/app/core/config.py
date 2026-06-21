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
    bcrypt_rounds: int = Field(default=12, ge=4, le=18, alias="BCRYPT_ROUNDS")

    # --- CORS --------------------------------------------------------------
    # ``NoDecode`` stops pydantic-settings from JSON-decoding the env value so
    # the validator below can accept a plain comma-separated string.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"], alias="CORS_ORIGINS"
    )

    # --- Uploads -----------------------------------------------------------
    upload_dir: str = Field(default="var/uploads", alias="UPLOAD_DIR")
    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024, alias="MAX_UPLOAD_SIZE_BYTES")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Allow a comma-separated string for CORS origins in env files."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
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
