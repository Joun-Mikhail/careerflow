"""Integration tests for the dashboard summary endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_application(
    client: TestClient, headers: dict[str, str], status: str = "applied"
) -> str:
    response = client.post(
        "/api/v1/applications",
        json={"role_title": "Engineer", "status": status},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_summary_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard/summary").status_code == 401


def test_empty_summary(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = client.get("/api/v1/dashboard/summary", headers=auth_headers).json()
    assert body["totals"]["applications"] == 0
    assert body["success_rate"] == 0.0
    assert body["upcoming_interviews"] == []
    assert body["pending_tasks"] == []
    assert body["recent_applications"] == []


def test_totals_and_success_rate(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_application(client, auth_headers, status="applied")
    _create_application(client, auth_headers, status="offer")
    _create_application(client, auth_headers, status="accepted")
    _create_application(client, auth_headers, status="rejected")
    body = client.get("/api/v1/dashboard/summary", headers=auth_headers).json()
    totals = body["totals"]
    assert totals["applications"] == 4
    assert totals["offers"] == 1
    assert totals["accepted"] == 1
    assert totals["rejections"] == 1
    # (offer + accepted) / total = 2/4 = 50%
    assert body["success_rate"] == 50.0


def test_upcoming_interviews_listed(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    client.post(
        f"/api/v1/applications/{app_id}/interviews",
        json={"scheduled_at": "2099-01-01T10:00:00Z", "interviewer": "Sam"},
        headers=auth_headers,
    )
    body = client.get("/api/v1/dashboard/summary", headers=auth_headers).json()
    assert body["totals"]["interviews"] == 1
    assert len(body["upcoming_interviews"]) == 1
    assert body["upcoming_interviews"][0]["role_title"] == "Engineer"


def test_pending_tasks_listed(client: TestClient, auth_headers: dict[str, str]) -> None:
    client.post("/api/v1/tasks", json={"title": "Follow up"}, headers=auth_headers)
    body = client.get("/api/v1/dashboard/summary", headers=auth_headers).json()
    assert body["totals"]["pending_tasks"] == 1
    assert body["pending_tasks"][0]["title"] == "Follow up"
