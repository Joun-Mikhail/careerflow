"""Integration tests for interview endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_application(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post("/api/v1/applications", json={"role_title": "Engineer"}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_interview(
    client: TestClient, headers: dict[str, str], application_id: str, **overrides: object
) -> dict:
    payload: dict[str, object] = {"scheduled_at": "2026-07-01T10:00:00Z", "mode": "video"}
    payload.update(overrides)
    response = client.post(
        f"/api/v1/applications/{application_id}/interviews", json=payload, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_interview(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    body = _create_interview(client, auth_headers, app_id, interviewer="Jordan", round_type="Phone")
    assert body["application_id"] == app_id
    assert body["interviewer"] == "Jordan"
    assert body["result"] == "pending"


def test_create_on_unowned_application_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/applications/00000000-0000-0000-0000-000000000000/interviews",
        json={"scheduled_at": "2026-07-01T10:00:00Z"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_list_interviews_ordered_by_schedule(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    app_id = _create_application(client, auth_headers)
    _create_interview(client, auth_headers, app_id, scheduled_at="2026-08-01T10:00:00Z")
    _create_interview(client, auth_headers, app_id, scheduled_at="2026-07-01T10:00:00Z")
    response = client.get(f"/api/v1/applications/{app_id}/interviews", headers=auth_headers)
    assert response.status_code == 200
    dates = [item["scheduled_at"] for item in response.json()]
    assert dates == sorted(dates)


def test_update_interview_result(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    interview = _create_interview(client, auth_headers, app_id)
    response = client.patch(
        f"/api/v1/interviews/{interview['id']}",
        json={"result": "passed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["result"] == "passed"


def test_delete_interview(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    interview = _create_interview(client, auth_headers, app_id)
    assert (
        client.delete(f"/api/v1/interviews/{interview['id']}", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.get(f"/api/v1/interviews/{interview['id']}", headers=auth_headers).status_code == 404
    )


def test_global_list_and_scope_filters(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _create_interview(client, auth_headers, app_id, scheduled_at="2099-01-01T10:00:00Z")
    _create_interview(client, auth_headers, app_id, scheduled_at="2000-01-01T10:00:00Z")

    all_body = client.get("/api/v1/interviews", headers=auth_headers).json()
    assert all_body["total"] == 2

    upcoming = client.get("/api/v1/interviews?scope=upcoming", headers=auth_headers).json()
    assert upcoming["total"] == 1
    assert upcoming["items"][0]["scheduled_at"].startswith("2099")

    past = client.get("/api/v1/interviews?scope=past", headers=auth_headers).json()
    assert past["total"] == 1
    assert past["items"][0]["scheduled_at"].startswith("2000")


def test_global_list_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _create_interview(client, auth_headers, app_id)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "iv-other@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    body = client.get("/api/v1/interviews", headers=other_headers).json()
    assert body["total"] == 0


def test_invalid_mode_rejected(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = client.post(
        f"/api/v1/applications/{app_id}/interviews",
        json={"scheduled_at": "2026-07-01T10:00:00Z", "mode": "telepathy"},
        headers=auth_headers,
    )
    assert response.status_code == 422
