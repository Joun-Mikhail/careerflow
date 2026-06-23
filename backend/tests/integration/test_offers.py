"""Integration tests for offer endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_application(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post("/api/v1/applications", json={"role_title": "Engineer"}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _create_offer(
    client: TestClient, headers: dict[str, str], application_id: str, **overrides: object
) -> dict:
    payload: dict[str, object] = {"base_salary": 150000, "currency": "USD"}
    payload.update(overrides)
    response = client.post(
        f"/api/v1/applications/{application_id}/offers", json=payload, headers=headers
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_offer(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    body = _create_offer(client, auth_headers, app_id, bonus=20000, benefits="Health, 401k")
    assert body["application_id"] == app_id
    assert body["base_salary"] == 150000
    assert body["decision"] == "pending"
    assert body["benefits"] == "Health, 401k"


def test_create_on_unowned_application_returns_404(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/applications/00000000-0000-0000-0000-000000000000/offers",
        json={"base_salary": 1},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_create_rejects_negative_salary(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    response = client.post(
        f"/api/v1/applications/{app_id}/offers",
        json={"base_salary": -5},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_list_offers_globally(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _create_offer(client, auth_headers, app_id)
    _create_offer(client, auth_headers, app_id, base_salary=160000)
    body = client.get("/api/v1/offers", headers=auth_headers).json()
    assert body["total"] == 2


def test_list_offers_filter_by_decision(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    accepted = _create_offer(client, auth_headers, app_id)
    _create_offer(client, auth_headers, app_id)
    client.patch(
        f"/api/v1/offers/{accepted['id']}", json={"decision": "accepted"}, headers=auth_headers
    )
    body = client.get("/api/v1/offers?decision=accepted", headers=auth_headers).json()
    assert body["total"] == 1


def test_list_for_application(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _create_offer(client, auth_headers, app_id)
    listing = client.get(f"/api/v1/applications/{app_id}/offers", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_update_decision(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    offer = _create_offer(client, auth_headers, app_id)
    response = client.patch(
        f"/api/v1/offers/{offer['id']}", json={"decision": "declined"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["decision"] == "declined"


def test_delete_offer(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    offer = _create_offer(client, auth_headers, app_id)
    assert client.delete(f"/api/v1/offers/{offer['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/v1/offers/{offer['id']}", headers=auth_headers).status_code == 404


def test_offers_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    app_id = _create_application(client, auth_headers)
    _create_offer(client, auth_headers, app_id)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "offers-other@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    body = client.get("/api/v1/offers", headers=other_headers).json()
    assert body["total"] == 0
