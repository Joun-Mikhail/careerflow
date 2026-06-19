"""Integration tests for company endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload = {"name": "Acme Corp", "industry": "Software", "location": "Remote"}
    payload.update(overrides)
    response = client.post("/api/v1/companies", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_company(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = _create(client, auth_headers, name="Globex")
    assert body["name"] == "Globex"
    assert body["id"]
    assert body["created_at"]


def test_create_requires_authentication(client: TestClient) -> None:
    assert client.post("/api/v1/companies", json={"name": "X"}).status_code == 401


def test_create_validates_blank_name(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/api/v1/companies", json={"name": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_get_company(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create(client, auth_headers)
    response = client.get(f"/api/v1/companies/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Acme Corp"


def test_get_missing_company_returns_404(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get(
        "/api/v1/companies/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_update_company(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create(client, auth_headers)
    response = client.patch(
        f"/api/v1/companies/{created['id']}",
        json={"location": "Berlin"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["location"] == "Berlin"
    assert body["name"] == "Acme Corp"  # unchanged


def test_delete_company_is_soft_and_hidden_afterwards(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = _create(client, auth_headers)
    assert (
        client.delete(f"/api/v1/companies/{created['id']}", headers=auth_headers).status_code == 204
    )
    # Soft-deleted companies are not retrievable or listed.
    assert client.get(f"/api/v1/companies/{created['id']}", headers=auth_headers).status_code == 404
    listing = client.get("/api/v1/companies", headers=auth_headers).json()
    assert listing["total"] == 0


def test_list_pagination(client: TestClient, auth_headers: dict[str, str]) -> None:
    for i in range(5):
        _create(client, auth_headers, name=f"Company {i}")
    response = client.get("/api/v1/companies?page=1&page_size=2", headers=auth_headers)
    body = response.json()
    assert body["total"] == 5
    assert body["total_pages"] == 3
    assert len(body["items"]) == 2


def test_list_search_by_name(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create(client, auth_headers, name="Stripe")
    _create(client, auth_headers, name="Square")
    body = client.get("/api/v1/companies?q=stri", headers=auth_headers).json()
    assert body["total"] == 1
    assert body["items"][0]["name"] == "Stripe"


def test_list_filter_by_industry(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create(client, auth_headers, name="A", industry="Fintech")
    _create(client, auth_headers, name="B", industry="Health")
    body = client.get("/api/v1/companies?industry=Fintech", headers=auth_headers).json()
    assert body["total"] == 1


def test_list_sort_by_name_asc(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create(client, auth_headers, name="Zebra")
    _create(client, auth_headers, name="Alpha")
    body = client.get("/api/v1/companies?sort=name&order=asc", headers=auth_headers).json()
    names = [item["name"] for item in body["items"]]
    assert names == ["Alpha", "Zebra"]


def test_companies_are_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create(client, auth_headers, name="Owned")
    # A second user sees none of the first user's companies.
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    body = client.get("/api/v1/companies", headers=other_headers).json()
    assert body["total"] == 0
