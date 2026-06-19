"""Integration tests for task endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_task(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload: dict[str, object] = {"title": "Follow up", "priority": "medium"}
    payload.update(overrides)
    response = client.post("/api/v1/tasks", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_task(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = _create_task(client, auth_headers, title="Send thank-you note")
    assert body["title"] == "Send thank-you note"
    assert body["is_completed"] is False
    assert body["completed_at"] is None


def test_complete_task_sets_timestamp(client: TestClient, auth_headers: dict[str, str]) -> None:
    task = _create_task(client, auth_headers)
    response = client.post(f"/api/v1/tasks/{task['id']}/complete", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["is_completed"] is True
    assert body["completed_at"] is not None


def test_uncompleting_via_patch_clears_timestamp(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    task = _create_task(client, auth_headers)
    client.post(f"/api/v1/tasks/{task['id']}/complete", headers=auth_headers)
    response = client.patch(
        f"/api/v1/tasks/{task['id']}", json={"is_completed": False}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["completed_at"] is None


def test_filter_by_completion(client: TestClient, auth_headers: dict[str, str]) -> None:
    done = _create_task(client, auth_headers, title="Done")
    _create_task(client, auth_headers, title="Pending")
    client.post(f"/api/v1/tasks/{done['id']}/complete", headers=auth_headers)
    body = client.get("/api/v1/tasks?is_completed=true", headers=auth_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Done"


def test_filter_by_priority(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_task(client, auth_headers, title="Urgent", priority="high")
    _create_task(client, auth_headers, title="Whenever", priority="low")
    body = client.get("/api/v1/tasks?priority=high", headers=auth_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Urgent"


def test_sort_by_priority_descending_is_semantic(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _create_task(client, auth_headers, title="Low", priority="low")
    _create_task(client, auth_headers, title="High", priority="high")
    _create_task(client, auth_headers, title="Medium", priority="medium")
    body = client.get("/api/v1/tasks?sort=priority&order=desc", headers=auth_headers).json()
    priorities = [item["priority"] for item in body["items"]]
    assert priorities == ["high", "medium", "low"]


def test_create_with_unowned_application_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"title": "X", "application_id": "00000000-0000-0000-0000-000000000000"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_task(client: TestClient, auth_headers: dict[str, str]) -> None:
    task = _create_task(client, auth_headers)
    assert client.delete(f"/api/v1/tasks/{task['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers).status_code == 404
