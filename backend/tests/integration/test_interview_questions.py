"""Integration tests for the interview question bank."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload: dict[str, object] = {"question": "Tell me about a hard bug you fixed."}
    payload.update(overrides)
    response = client.post("/api/v1/interview-questions", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _create_application(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/applications",
        json={"role_title": "Backend Engineer"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_update_delete(client: TestClient, auth_headers: dict[str, str]) -> None:
    created = _create(client, auth_headers, tags="behavioural", answer="The N+1 query one.")
    assert created["asked"] is False
    assert created["answer"] == "The N+1 query one."

    listing = client.get("/api/v1/interview-questions", headers=auth_headers).json()
    assert len(listing) == 1

    patched = client.patch(
        f"/api/v1/interview-questions/{created['id']}",
        json={"asked": True, "answer": "Refined answer."},
        headers=auth_headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["asked"] is True
    assert patched.json()["answer"] == "Refined answer."

    assert (
        client.delete(
            f"/api/v1/interview-questions/{created['id']}", headers=auth_headers
        ).status_code
        == 204
    )
    assert client.get("/api/v1/interview-questions", headers=auth_headers).json() == []


class TestTags:
    def test_tags_are_normalised(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        created = _create(client, auth_headers, tags="  System Design ,BEHAVIOURAL,  ")
        assert created["tags"] == "system design, behavioural"

    def test_duplicate_tags_collapse(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        created = _create(client, auth_headers, tags="sql, SQL, sql")
        assert created["tags"] == "sql"

    def test_blank_tags_become_null(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        created = _create(client, auth_headers, tags="  ,  ")
        assert created["tags"] is None

    def test_filter_by_tag(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        _create(client, auth_headers, question="Design a URL shortener.", tags="system design")
        _create(client, auth_headers, question="Why leave your last role?", tags="behavioural")

        filtered = client.get(
            "/api/v1/interview-questions", params={"tag": "behavioural"}, headers=auth_headers
        ).json()
        assert len(filtered) == 1
        assert filtered[0]["question"] == "Why leave your last role?"

    def test_tag_filter_does_not_match_substrings(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        # "sql" must not match a question tagged only "graphql".
        _create(client, auth_headers, question="Explain resolvers.", tags="graphql")
        filtered = client.get(
            "/api/v1/interview-questions", params={"tag": "sql"}, headers=auth_headers
        ).json()
        assert filtered == []


class TestApplicationLink:
    def test_filter_by_application(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        application = _create_application(client, auth_headers)
        _create(client, auth_headers, question="Linked", application_id=application["id"])
        _create(client, auth_headers, question="Unlinked")

        filtered = client.get(
            "/api/v1/interview-questions",
            params={"application_id": application["id"]},
            headers=auth_headers,
        ).json()
        assert len(filtered) == 1
        assert filtered[0]["question"] == "Linked"

    def test_cannot_link_to_another_users_application(
        self, client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        application = _create_application(client, auth_headers)
        other = client.post(
            "/api/v1/auth/register",
            json={"email": "nosy@example.com", "password": "Sup3rSecret!", "full_name": "N"},
        ).json()
        intruder = {"Authorization": f"Bearer {other['token']['access_token']}"}

        response = client.post(
            "/api/v1/interview-questions",
            json={"question": "Sneaky", "application_id": application["id"]},
            headers=intruder,
        )
        assert response.status_code == 404


def test_questions_are_scoped_to_their_owner(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = _create(client, auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "stranger@example.com", "password": "Sup3rSecret!", "full_name": "S"},
    ).json()
    intruder = {"Authorization": f"Bearer {other['token']['access_token']}"}

    assert client.get("/api/v1/interview-questions", headers=intruder).json() == []
    assert (
        client.patch(
            f"/api/v1/interview-questions/{created['id']}",
            json={"asked": True},
            headers=intruder,
        ).status_code
        == 404
    )


def test_question_is_required(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/interview-questions", json={"answer": "orphan"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/interview-questions").status_code == 401


def test_cannot_relink_a_question_to_another_users_application(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """The ownership check must run on update, not only on create."""
    question = _create(client, auth_headers)

    other = client.post(
        "/api/v1/auth/register",
        json={"email": "rival2@example.com", "password": "Sup3rSecret!", "full_name": "R"},
    ).json()
    rival_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    rival_application = _create_application(client, rival_headers)

    response = client.patch(
        f"/api/v1/interview-questions/{question['id']}",
        json={"application_id": rival_application["id"]},
        headers=auth_headers,
    )
    assert response.status_code == 404
