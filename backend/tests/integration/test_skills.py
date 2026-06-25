"""Integration tests for skill endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_create_and_list_skills(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/skills",
        json={"name": "Python", "category": "Languages", "proficiency": "expert"},
        headers=auth_headers,
    )
    assert created.status_code == 201, created.text
    assert created.json()["name"] == "Python"

    listing = client.get("/api/v1/skills", headers=auth_headers).json()
    assert [s["name"] for s in listing] == ["Python"]


def test_duplicate_skill_name_rejected(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/api/v1/skills", json={"name": "Go"}, headers=auth_headers)
    dup = client.post("/api/v1/skills", json={"name": "go"}, headers=auth_headers)
    assert dup.status_code == 409


def test_update_and_delete_skill(client: TestClient, auth_headers: dict[str, str]) -> None:
    skill_id = client.post("/api/v1/skills", json={"name": "Rust"}, headers=auth_headers).json()[
        "id"
    ]

    patched = client.patch(
        f"/api/v1/skills/{skill_id}",
        json={"proficiency": "advanced"},
        headers=auth_headers,
    )
    assert patched.status_code == 200
    assert patched.json()["proficiency"] == "advanced"

    assert client.delete(f"/api/v1/skills/{skill_id}", headers=auth_headers).status_code == 204
    assert client.get("/api/v1/skills", headers=auth_headers).json() == []


def test_skills_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/api/v1/skills", json={"name": "SQL"}, headers=auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "skills-other@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    assert client.get("/api/v1/skills", headers=other_headers).json() == []
