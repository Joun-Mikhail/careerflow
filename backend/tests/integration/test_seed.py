"""Tests for the demo data seeding routine."""

from __future__ import annotations

from app.repositories.user import UserRepository
from app.seed import DEMO_EMAIL, seed_demo_data
from sqlalchemy.orm import Session


def test_seed_creates_demo_user_and_data(db_session: Session) -> None:
    assert seed_demo_data(db_session) is True
    user = UserRepository(db_session).get_by_email(DEMO_EMAIL)
    assert user is not None
    assert user.full_name == "Demo Candidate"
    assert len(user.companies) == 6
    assert len(user.applications) == 8


def test_seed_is_idempotent(db_session: Session) -> None:
    assert seed_demo_data(db_session) is True
    # A second run must not duplicate data.
    assert seed_demo_data(db_session) is False
    user = UserRepository(db_session).get_by_email(DEMO_EMAIL)
    assert user is not None
    assert len(user.applications) == 8


def test_seeded_user_can_log_in(db_session: Session, client) -> None:
    seed_demo_data(db_session)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_EMAIL, "password": "DemoPass123!"},
    )
    assert response.status_code == 200
    assert response.json()["token"]["access_token"]
