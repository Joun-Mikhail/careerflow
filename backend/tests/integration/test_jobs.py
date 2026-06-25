"""Integration tests for job-search filters and fetching (mock provider)."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _create_filter(client: TestClient, headers: dict[str, str], **overrides: object) -> dict:
    payload: dict[str, object] = {"name": "Remote backend", "title_keywords": "Python Engineer"}
    payload.update(overrides)
    response = client.post("/api/v1/job-filters", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_list_update_delete_filter(client: TestClient, auth_headers: dict[str, str]) -> None:
    filt = _create_filter(client, auth_headers, remote=True, salary_min=80000)
    assert filt["remote"] is True

    listing = client.get("/api/v1/job-filters", headers=auth_headers).json()
    assert len(listing) == 1

    patched = client.patch(
        f"/api/v1/job-filters/{filt['id']}", json={"name": "Renamed"}, headers=auth_headers
    )
    assert patched.json()["name"] == "Renamed"

    assert (
        client.delete(f"/api/v1/job-filters/{filt['id']}", headers=auth_headers).status_code == 204
    )
    assert client.get("/api/v1/job-filters", headers=auth_headers).json() == []


def test_run_search_stores_and_lists_jobs(client: TestClient, auth_headers: dict[str, str]) -> None:
    filt = _create_filter(client, auth_headers, title_keywords="Data Engineer")
    results = client.post(f"/api/v1/job-filters/{filt['id']}/search", headers=auth_headers)
    assert results.status_code == 200, results.text
    jobs = results.json()
    assert len(jobs) > 0
    assert jobs[0]["source"] == "mock"  # no Adzuna keys in tests
    assert "Data Engineer" in jobs[0]["title"]

    listed = client.get("/api/v1/jobs", headers=auth_headers).json()
    assert len(listed) == len(jobs)


def test_search_is_idempotent_on_dedup(client: TestClient, auth_headers: dict[str, str]) -> None:
    filt = _create_filter(client, auth_headers)
    first = client.post(f"/api/v1/job-filters/{filt['id']}/search", headers=auth_headers).json()
    client.post(f"/api/v1/job-filters/{filt['id']}/search", headers=auth_headers)
    listed = client.get("/api/v1/jobs", headers=auth_headers).json()
    # Re-running the same filter updates rather than duplicates.
    assert len(listed) == len(first)


def test_tailor_cv_from_job_id(client: TestClient, auth_headers: dict[str, str]) -> None:
    filt = _create_filter(client, auth_headers, title_keywords="Platform Engineer")
    jobs = client.post(f"/api/v1/job-filters/{filt['id']}/search", headers=auth_headers).json()
    job_id = jobs[0]["id"]

    response = client.post(
        "/api/v1/ai/tailor-cv",
        json={"cv_text": "Experienced platform engineer.", "job_id": job_id},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["tailored_cv"]


def test_filters_scoped_to_owner(client: TestClient, auth_headers: dict[str, str]) -> None:
    _create_filter(client, auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "jobs-other@example.com", "password": "Sup3rSecret!"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}
    assert client.get("/api/v1/job-filters", headers=other_headers).json() == []
    assert client.get("/api/v1/jobs", headers=other_headers).json() == []
