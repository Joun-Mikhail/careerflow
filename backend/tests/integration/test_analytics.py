"""Integration tests for analytics endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_application(
    client: TestClient,
    headers: dict[str, str],
    *,
    status: str = "applied",
    company_id: str | None = None,
) -> str:
    payload: dict[str, object] = {"role_title": "Engineer", "status": status}
    if company_id:
        payload["company_id"] = company_id
    response = client.post("/api/v1/applications", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_applications_by_month_returns_12_buckets(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _create_application(client, auth_headers)
    body = client.get("/api/v1/analytics/applications-by-month", headers=auth_headers).json()
    assert len(body["items"]) == 12
    # The most recent month should include the application just created.
    assert body["items"][-1]["count"] == 1


def test_status_distribution_covers_all_statuses(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    _create_application(client, auth_headers, status="offer")
    body = client.get("/api/v1/analytics/status-distribution", headers=auth_headers).json()
    statuses = {item["status"]: item["count"] for item in body["items"]}
    assert statuses["offer"] == 1
    assert statuses["applied"] == 0
    assert len(body["items"]) == 8  # all enum members represented


def test_industry_distribution(client: TestClient, auth_headers: dict[str, str]) -> None:
    company = client.post(
        "/api/v1/companies",
        json={"name": "Acme", "industry": "Fintech"},
        headers=auth_headers,
    ).json()
    _create_application(client, auth_headers, company_id=company["id"])
    body = client.get("/api/v1/analytics/industry-distribution", headers=auth_headers).json()
    assert body["items"] == [{"industry": "Fintech", "count": 1}]


def test_conversion_rates(client: TestClient, auth_headers: dict[str, str]) -> None:
    app1 = _create_application(client, auth_headers, status="offer")
    _create_application(client, auth_headers, status="applied")
    # Add an interview to one application -> interview_rate 1/2 = 50%.
    client.post(
        f"/api/v1/applications/{app1}/interviews",
        json={"scheduled_at": "2026-07-01T10:00:00Z"},
        headers=auth_headers,
    )
    body = client.get("/api/v1/analytics/conversion", headers=auth_headers).json()
    assert body["total_applications"] == 2
    assert body["interview_rate"] == 50.0
    assert body["offer_rate"] == 50.0  # one offer of two


def test_conversion_empty_is_zero(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = client.get("/api/v1/analytics/conversion", headers=auth_headers).json()
    assert body["total_applications"] == 0
    assert body["interview_rate"] == 0.0
    assert body["offer_rate"] == 0.0


def test_analytics_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/analytics/conversion").status_code == 401
