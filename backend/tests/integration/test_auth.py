"""Integration tests for the authentication endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert body["version"]
    assert "uptime_seconds" in body


def test_register_returns_user_and_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "Sup3rSecret!", "full_name": "New User"},
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert "hashed_password" not in body["user"]
    assert body["token"]["access_token"]
    assert body["token"]["token_type"] == "bearer"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {"email": "dupe@example.com", "password": "Sup3rSecret!"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    conflict = client.post("/api/v1/auth/register", json=payload)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "conflict"


def test_register_is_email_case_insensitive(client: TestClient) -> None:
    assert (
        client.post(
            "/api/v1/auth/register",
            json={"email": "Mixed@Example.com", "password": "Sup3rSecret!"},
        ).status_code
        == 201
    )
    conflict = client.post(
        "/api/v1/auth/register",
        json={"email": "mixed@example.com", "password": "Sup3rSecret!"},
    )
    assert conflict.status_code == 409


def test_register_validates_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "x"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_login_succeeds_with_correct_credentials(
    client: TestClient, registered_user: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    assert response.json()["token"]["access_token"]


def test_login_rejects_wrong_password(client: TestClient, registered_user: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_rejects_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "whatever123"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_profile_with_token(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "alex@example.com"


def test_me_rejects_garbage_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert response.status_code == 401


def test_login_returns_refresh_token(client: TestClient, registered_user: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    assert response.json()["token"]["refresh_token"]


def test_refresh_returns_new_tokens(client: TestClient, registered_user: dict[str, str]) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    ).json()
    refresh_token = login["token"]["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert body["token"]["access_token"]
    assert body["token"]["refresh_token"]
    # The new access token authorizes a protected route.
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['token']['access_token']}"},
    )
    assert me.status_code == 200


def test_refresh_rejects_access_token(client: TestClient, registered_user: dict[str, str]) -> None:
    # Passing an access token where a refresh token is expected must fail.
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": registered_user["token"]})
    assert response.status_code == 401


def test_refresh_rejects_garbage(client: TestClient) -> None:
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "not.a.jwt"})
    assert response.status_code == 401


def test_update_profile(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.patch(
        "/api/v1/auth/me", json={"full_name": "Alex Renamed"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Alex Renamed"


def test_change_password_then_login_with_new(
    client: TestClient, registered_user: dict[str, str], auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": registered_user["password"], "new_password": "BrandNew1!"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    old = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": registered_user["password"]},
    )
    assert old.status_code == 401
    new = client.post(
        "/api/v1/auth/login",
        json={"email": registered_user["email"], "password": "BrandNew1!"},
    )
    assert new.status_code == 200


def test_change_password_rejects_wrong_current(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong-one", "new_password": "BrandNew1!"},
        headers=auth_headers,
    )
    assert response.status_code == 401


def test_change_password_validates_new_length(
    client: TestClient, registered_user: dict[str, str], auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": registered_user["password"], "new_password": "short"},
        headers=auth_headers,
    )
    assert response.status_code == 422
