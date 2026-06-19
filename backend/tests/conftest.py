"""Shared pytest fixtures.

Tests run against an in-memory SQLite database created fresh for each test, so
the suite is fast, isolated, and requires no external services. A ``StaticPool``
keeps a single connection alive so the schema persists across the TestClient's
worker threads.
"""

from __future__ import annotations

import os

# Configure a deterministic, test-only environment *before* importing any app
# module, since settings are parsed and cached on first import.
os.environ.setdefault("CAREERFLOW_ENV", "test")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("JWT_SECRET", "test-secret-key-at-least-32-bytes-long-000")
os.environ.setdefault("DATABASE_URL", "sqlite://")

from collections.abc import Iterator

import app.models
import pytest
from app.core.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory database session per test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """A TestClient whose requests use the test database session."""

    def override_get_db() -> Iterator[Session]:
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client: TestClient) -> dict[str, str]:
    """Register a user and return credentials plus a bearer token."""
    payload = {
        "email": "alex@example.com",
        "password": "Sup3rSecret!",
        "full_name": "Alex Doe",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    return {
        "email": payload["email"],
        "password": payload["password"],
        "token": body["token"]["access_token"],
        "user_id": body["user"]["id"],
    }


@pytest.fixture
def auth_headers(registered_user: dict[str, str]) -> dict[str, str]:
    """Authorization header for the registered user."""
    return {"Authorization": f"Bearer {registered_user['token']}"}
