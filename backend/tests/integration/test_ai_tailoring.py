"""Integration tests for the AI CV-tailoring endpoint (uses the stub provider)."""

from __future__ import annotations

from fastapi.testclient import TestClient

JOB = "We need a senior Python backend engineer with FastAPI and PostgreSQL experience."
CV_TEXT = "Jane Doe. Backend engineer. Built APIs in Python and Postgres for 6 years."


def test_tailor_from_pasted_text(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ai/tailor-cv",
        json={"cv_text": CV_TEXT, "job_description": JOB},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["provider"] == "stub"  # no key configured in tests
    assert CV_TEXT.strip() in body["tailored_cv"]
    assert body["cover_letter"] is None
    assert body["saved_cv_id"] is None


def test_tailor_with_cover_letter(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ai/tailor-cv",
        json={"cv_text": CV_TEXT, "job_description": JOB, "include_cover_letter": True},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["cover_letter"]


def test_tailor_and_save_creates_new_cv(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ai/tailor-cv",
        json={"cv_text": CV_TEXT, "job_description": JOB, "save_as_title": "Tailored — Acme"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    saved_id = response.json()["saved_cv_id"]
    assert saved_id is not None

    cvs = client.get("/api/v1/cvs", headers=auth_headers).json()
    saved = next(c for c in cvs if c["id"] == saved_id)
    assert saved["source"] == "ai_tailored"
    assert saved["title"] == "Tailored — Acme"


def test_tailor_requires_a_base(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/ai/tailor-cv", json={"job_description": JOB}, headers=auth_headers
    )
    assert response.status_code == 422  # neither cv_id nor cv_text


def test_tailor_from_cv_without_text_is_rejected(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    # An uploaded (file-backed) CV has no content_text to tailor from.
    cv_id = client.post(
        "/api/v1/cvs",
        files={"file": ("cv.pdf", b"%PDF-1.4 bytes", "application/pdf")},
        headers=auth_headers,
    ).json()["id"]

    response = client.post(
        "/api/v1/ai/tailor-cv",
        json={"cv_id": cv_id, "job_description": JOB},
        headers=auth_headers,
    )
    assert response.status_code == 422
