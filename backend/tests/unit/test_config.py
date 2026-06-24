"""Unit tests for settings parsing."""

from __future__ import annotations

import pytest
from app.core.config import Settings


def test_cors_origins_parses_comma_separated_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173,https://app.example.com")
    settings = Settings()
    assert settings.cors_origins == ["http://localhost:5173", "https://app.example.com"]


def test_cors_origins_strips_whitespace_and_blanks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", " http://a.test , , http://b.test ")
    settings = Settings()
    assert settings.cors_origins == ["http://a.test", "http://b.test"]


def test_production_rejects_placeholder_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CAREERFLOW_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "change-me-in-production")
    with pytest.raises(RuntimeError):
        Settings().validate_for_runtime()


def test_database_url_picks_psycopg_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/db")
    assert Settings().database_url == "postgresql+psycopg://user:pass@host:5432/db"


def test_database_url_rewrites_heroku_legacy_scheme(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h:5432/d")
    assert Settings().database_url == "postgresql+psycopg://u:p@h:5432/d"


def test_database_url_preserves_explicit_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://u:p@h:5432/d")
    assert Settings().database_url == "postgresql+psycopg://u:p@h:5432/d"


def test_database_url_passes_through_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    assert Settings().database_url == "sqlite:///./test.db"
