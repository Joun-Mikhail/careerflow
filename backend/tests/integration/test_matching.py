"""Integration tests for the CV-to-job match-scoring endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

JOB = (
    "Senior Python backend engineer. You will build FastAPI services on "
    "PostgreSQL, deploy with Docker on AWS, and work with Kubernetes."
)
STRONG_CV = (
    "Senior backend engineer. Six years of Python and FastAPI on PostgreSQL, "
    "shipping with Docker to AWS and Kubernetes."
)
WEAK_CV = "Pastry chef. I run a bakery, design seasonal menus and manage suppliers."


def _search_jobs(client: TestClient, headers: dict[str, str]) -> list[dict]:
    """Run a search so there are stored jobs to score against."""
    filt = client.post(
        "/api/v1/job-filters",
        json={"name": "Backend", "title_keywords": "Python Engineer"},
        headers=headers,
    ).json()
    response = client.post(f"/api/v1/job-filters/{filt['id']}/search", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_score_against_a_pasted_job_description(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/matching/score",
        json={"cv_text": STRONG_CV, "job_description": JOB},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    results = response.json()["results"]
    assert len(results) == 1

    match = results[0]
    assert match["job_id"] is None  # inline description, not a stored job
    assert match["score"] >= 75
    assert match["verdict"] == "strong"
    assert "python" in match["matched_skills"]
    assert set(match["breakdown"]) == {"skills", "keywords", "seniority"}


def test_a_weaker_cv_scores_lower_on_the_same_job(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    def score(cv: str) -> int:
        response = client.post(
            "/api/v1/matching/score",
            json={"cv_text": cv, "job_description": JOB},
            headers=auth_headers,
        )
        return response.json()["results"][0]["score"]

    assert score(WEAK_CV) < score(STRONG_CV)


def test_score_against_stored_jobs_ranks_strongest_first(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    jobs = _search_jobs(client, auth_headers)
    job_ids = [job["id"] for job in jobs]

    response = client.post(
        "/api/v1/matching/score",
        json={"cv_text": STRONG_CV, "job_ids": job_ids},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    results = response.json()["results"]
    assert len(results) == len(job_ids)
    assert [r["job_id"] for r in results if r["job_id"]] != []

    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_unknown_job_ids_are_skipped_not_fatal(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    jobs = _search_jobs(client, auth_headers)
    unknown = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        "/api/v1/matching/score",
        json={"cv_text": STRONG_CV, "job_ids": [jobs[0]["id"], unknown]},
        headers=auth_headers,
    )
    assert response.status_code == 200, response.text
    # The real job is still scored; the unknown one is simply absent.
    assert len(response.json()["results"]) == 1


def test_only_unknown_job_ids_is_a_clear_error(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/matching/score",
        json={"cv_text": STRONG_CV, "job_ids": ["00000000-0000-0000-0000-000000000000"]},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_scoring_requires_a_cv(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/matching/score", json={"job_description": JOB}, headers=auth_headers
    )
    assert response.status_code == 422


def test_scoring_requires_a_target(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/matching/score", json={"cv_text": STRONG_CV}, headers=auth_headers
    )
    assert response.status_code == 422


def test_scoring_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/v1/matching/score", json={"cv_text": STRONG_CV, "job_description": JOB}
    )
    assert response.status_code == 401


def test_another_users_job_is_not_scorable(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    jobs = _search_jobs(client, auth_headers)
    other = client.post(
        "/api/v1/auth/register",
        json={"email": "intruder@example.com", "password": "Sup3rSecret!", "full_name": "I"},
    ).json()
    intruder_headers = {"Authorization": f"Bearer {other['token']['access_token']}"}

    response = client.post(
        "/api/v1/matching/score",
        json={"cv_text": STRONG_CV, "job_ids": [jobs[0]["id"]]},
        headers=intruder_headers,
    )
    # Scoped away, so it reads as "nothing to score" rather than leaking existence.
    assert response.status_code == 422
