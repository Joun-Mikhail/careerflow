"""Integration tests for contacts (recruiters, hiring managers, referrers)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload: dict[str, object] = {"name": "Dana Reed"}
    payload.update(overrides)
    response = client.post("/api/v1/contacts", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _create_company(client: TestClient, headers: dict[str, str], name: str = "Acme") -> dict:
    response = client.post("/api/v1/companies", json={"name": name}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_update_delete(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create(
        client,
        auth_headers,
        role="Technical Recruiter",
        email="dana@acme.io",
        notes="Met at a meetup.",
    )
    assert created["email"] == "dana@acme.io"

    listing = client.get("/api/v1/contacts", headers=auth_headers).json()
    assert len(listing) == 1

    patched = client.patch(
        f"/api/v1/contacts/{created['id']}",
        json={"role": "Head of Talent"},
        headers=auth_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["role"] == "Head of Talent"

    assert (
        client.delete(f"/api/v1/contacts/{created['id']}", headers=auth_headers).status_code == 204
    )
    assert client.get("/api/v1/contacts", headers=auth_headers).json() == []


def test_only_a_name_is_required(client: TestClient, auth_headers: dict[str, str]) -> None:
    # Contacts get captured mid-conversation, so everything else is optional.
    created = _create(client, auth_headers, name="Just A Name")
    assert created["email"] is None
    assert created["company_id"] is None


def test_a_malformed_email_is_rejected(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/contacts",
        json={"name": "Bad Email", "email": "not-an-email"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_listing_is_alphabetical_by_name(client: TestClient, auth_headers: dict[str, str]) -> None:
    for name in ("Zoe Adams", "alice Brown", "Marcus Chen"):
        _create(client, auth_headers, name=name)
    names = [c["name"] for c in client.get("/api/v1/contacts", headers=auth_headers).json()]
    assert names == ["alice Brown", "Marcus Chen", "Zoe Adams"]


class TestSearch:
    def test_search_matches_name_role_or_email(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        _create(client, auth_headers, name="Dana Reed", role="Recruiter")
        _create(client, auth_headers, name="Sam Patel", email="sam@northwind.io")

        by_role = client.get(
            "/api/v1/contacts", params={"search": "recruit"}, headers=auth_headers
        ).json()
        assert [c["name"] for c in by_role] == ["Dana Reed"]

        by_email = client.get(
            "/api/v1/contacts", params={"search": "northwind"}, headers=auth_headers
        ).json()
        assert [c["name"] for c in by_email] == ["Sam Patel"]

    def test_search_is_case_insensitive(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        _create(client, auth_headers, name="Dana Reed")
        found = client.get(
            "/api/v1/contacts", params={"search": "DANA"}, headers=auth_headers
        ).json()
        assert len(found) == 1


class TestCompanyLink:
    def test_filter_by_company(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        company = _create_company(client, auth_headers)
        _create(client, auth_headers, name="Linked", company_id=company["id"])
        _create(client, auth_headers, name="Unlinked")

        filtered = client.get(
            "/api/v1/contacts", params={"company_id": company["id"]}, headers=auth_headers
        ).json()
        assert [c["name"] for c in filtered] == ["Linked"]

    def test_cannot_link_to_another_users_company(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        company = _create_company(client, auth_headers)
        other = client.post(
            "/api/v1/auth/register",
            json={"email": "nosy2@example.com", "password": "Sup3rSecret!", "full_name": "N"},
        ).json()
        intruder = {"Authorization": f"Bearer {other['token']['access_token']}"}

        response = client.post(
            "/api/v1/contacts",
            json={"name": "Sneaky", "company_id": company["id"]},
            headers=intruder,
        )
        assert response.status_code == 404

    def test_deleting_a_company_keeps_its_contacts(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        company = _create_company(client, auth_headers)
        _create(client, auth_headers, name="Survivor", company_id=company["id"])

        assert (
            client.delete(f"/api/v1/companies/{company['id']}", headers=auth_headers).status_code
            == 204
        )

        remaining = client.get("/api/v1/contacts", headers=auth_headers).json()
        assert [c["name"] for c in remaining] == ["Survivor"]


def test_contacts_are_scoped_to_their_owner(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = _create(client, auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "stranger2@example.com", "password": "Sup3rSecret!", "full_name": "S"},
    ).json()
    intruder = {"Authorization": f"Bearer {other['token']['access_token']}"}

    assert client.get("/api/v1/contacts", headers=intruder).json() == []
    assert client.delete(f"/api/v1/contacts/{created['id']}", headers=intruder).status_code == 404


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/contacts").status_code == 401


def test_cannot_relink_a_contact_to_another_users_company(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """The ownership check must run on update, not only on create."""
    contact = _create(client, auth_headers, name="Dana Reed")

    other = client.post(
        "/api/v1/auth/register",
        json={"email": "rival@example.com", "password": "Sup3rSecret!", "full_name": "R"},
    ).json()
    rival_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    rival_company = _create_company(client, rival_headers, name="Rival Corp")

    response = client.patch(
        f"/api/v1/contacts/{contact['id']}",
        json={"company_id": rival_company["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 404
