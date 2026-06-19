"""Integration tests for note endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_application(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post("/api/v1/applications", json={"role_title": "Engineer"}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_and_list_notes(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    created = client.post(
        f"/api/v1/applications/{app_id}/notes",
        json={"body": "# Prep\nReview system design."},
        headers=auth_headers,
    )
    assert created.status_code == 201
    assert created.json()["body"].startswith("# Prep")

    listing = client.get(f"/api/v1/applications/{app_id}/notes", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_create_note_requires_body(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = client.post(
        f"/api/v1/applications/{app_id}/notes", json={"body": ""}, headers=auth_headers
    )
    assert response.status_code == 422


def test_note_on_unowned_application_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/applications/00000000-0000-0000-0000-000000000000/notes",
        json={"body": "hi"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_note(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    note = client.post(
        f"/api/v1/applications/{app_id}/notes",
        json={"body": "original"},
        headers=auth_headers,
    ).json()
    response = client.patch(
        f"/api/v1/notes/{note['id']}", json={"body": "edited"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["body"] == "edited"


def test_delete_note(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    note = client.post(
        f"/api/v1/applications/{app_id}/notes",
        json={"body": "to delete"},
        headers=auth_headers,
    ).json()
    assert client.delete(f"/api/v1/notes/{note['id']}", headers=auth_headers).status_code == 204
    listing = client.get(f"/api/v1/applications/{app_id}/notes", headers=auth_headers).json()
    assert listing == []
