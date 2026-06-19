"""Integration tests for job application endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_company(client: TestClient, headers: dict[str, str], name: str = "Acme") -> str:
    response = client.post("/api/v1/companies", json={"name": name}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_application(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload: dict[str, object] = {"role_title": "Backend Engineer", "status": "applied"}
    payload.update(overrides)
    response = client.post("/api/v1/applications", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_application_minimal(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = _create_application(client, auth_headers)
    assert body["role_title"] == "Backend Engineer"
    assert body["status"] == "applied"
    assert body["is_remote"] is False


def test_create_with_full_payload(client: TestClient, auth_headers: dict[str, str]) -> None:
    company_id = _create_company(client, auth_headers)
    body = _create_application(
        client,
        auth_headers,
        company_id=company_id,
        role_title="Senior Engineer",
        status="interview",
        salary_min=120000,
        salary_max=150000,
        salary_currency="USD",
        location="Remote",
        is_remote=True,
        application_url="https://example.com/jobs/1",
        source="LinkedIn",
    )
    assert body["company_id"] == company_id
    assert body["salary_max"] == 150000


def test_create_rejects_inverted_salary_range(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/applications",
        json={"role_title": "X", "salary_min": 100, "salary_max": 50},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_rejects_invalid_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/applications",
        json={"role_title": "X", "status": "not-a-status"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_create_with_unowned_company_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/applications",
        json={
            "role_title": "X",
            "company_id": "00000000-0000-0000-0000-000000000000",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_update_status_transition(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create_application(client, auth_headers, status="applied")
    response = client.patch(
        f"/api/v1/applications/{created['id']}",
        json={"status": "offer"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "offer"


def test_delete_is_soft(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create_application(client, auth_headers)
    assert (
        client.delete(f"/api/v1/applications/{created['id']}", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.get(f"/api/v1/applications/{created['id']}", headers=auth_headers).status_code == 404
    )


def test_list_filter_by_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_application(client, auth_headers, role_title="A", status="applied")
    _create_application(client, auth_headers, role_title="B", status="offer")
    body = client.get("/api/v1/applications?status=offer", headers=auth_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["role_title"] == "B"


def test_list_search_by_role(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_application(client, auth_headers, role_title="Data Scientist")
    _create_application(client, auth_headers, role_title="Product Manager")
    body = client.get("/api/v1/applications?q=scientist", headers=auth_headers).json()
    assert body["total"] == 1


def test_list_filter_by_company(client: TestClient, auth_headers: dict[str, str]) -> None:
    company_id = _create_company(client, auth_headers)
    _create_application(client, auth_headers, company_id=company_id)
    _create_application(client, auth_headers)  # no company
    body = client.get(f"/api/v1/applications?company_id={company_id}", headers=auth_headers).json()
    assert body["total"] == 1


def test_applications_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_application(client, auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "other2@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    body = client.get("/api/v1/applications", headers=other_headers).json()
    assert body["total"] == 0
