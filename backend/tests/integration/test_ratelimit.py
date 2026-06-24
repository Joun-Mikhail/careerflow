"""Integration test for auth rate limiting.

The limiter is disabled under the test profile so the rest of the suite can log
in freely; this test enables it explicitly and restores it afterwards.
"""

from __future__ import annotations

import contextlib

from app.core.ratelimit import limiter
from fastapi.testclient import TestClient


def test_auth_endpoints_are_rate_limited(client: TestClient) -> None:
    limiter.enabled = True
    try:
        client.post(
            "/api/v1/auth/register",
            json={"email": "rl@example.com", "password": "Sup3rSecret!"},
        )
        creds = {"email": "rl@example.com", "password": "Sup3rSecret!"}

        saw_rate_limit_headers = False
        rate_limited = None
        for _ in range(25):
            response = client.post("/api/v1/auth/login", json=creds)
            header_keys = {key.lower() for key in response.headers}
            if response.status_code == 200 and "x-ratelimit-limit" in header_keys:
                saw_rate_limit_headers = True
            if response.status_code == 429:
                rate_limited = response
                break

        assert saw_rate_limit_headers, "expected X-RateLimit headers on successful responses"
        assert rate_limited is not None, "expected a 429 once the limit was exceeded"
        assert rate_limited.json()["error"]["code"] == "rate_limited"
        assert "retry-after" in {key.lower() for key in rate_limited.headers}
    finally:
        limiter.enabled = False
        # The in-memory storage may not implement reset(); ignore if so.
        with contextlib.suppress(Exception):
            limiter.reset()
