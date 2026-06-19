"""Unit tests for password hashing and JWT token handling."""

from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest
from app.core.errors import AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_is_salted_and_verifiable() -> None:
    hashed = hash_password("Sup3rSecret!")
    assert hashed != "Sup3rSecret!"
    assert verify_password("Sup3rSecret!", hashed) is True


def test_hash_password_produces_distinct_hashes() -> None:
    assert hash_password("same-password") != hash_password("same-password")


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("correct-horse")
    assert verify_password("battery-staple", hashed) is False


def test_verify_password_handles_malformed_hash() -> None:
    assert verify_password("anything", "not-a-real-hash") is False


def test_access_token_round_trip() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    assert decode_access_token(token) == user_id


def test_expired_token_is_rejected() -> None:
    token = create_access_token(uuid4(), expires_delta=timedelta(seconds=-1))
    with pytest.raises(AuthenticationError):
        decode_access_token(token)


def test_garbage_token_is_rejected() -> None:
    with pytest.raises(AuthenticationError):
        decode_access_token("not.a.jwt")
