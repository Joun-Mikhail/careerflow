"""External job-source providers (Adzuna) with an offline mock fallback.

A :class:`JobProvider` turns a :class:`~app.models.job_search_filter.JobSearchFilter`
into a list of normalized :class:`JobPosting` results. ``AdzunaProvider`` calls
the Adzuna API (``httpx`` imported lazily); ``MockJobProvider`` returns
deterministic sample postings so the search flow works without credentials and
keeps tests hermetic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.core.config import get_settings
from app.models.job_search_filter import JobSearchFilter

settings = get_settings()

_ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs"


@dataclass(frozen=True)
class JobPosting:
    """A normalized job posting, independent of any source's response shape."""

    external_id: str
    title: str
    company: str | None
    location: str | None
    description: str | None
    url: str
    salary_min: int | None
    salary_max: int | None
    remote: bool
    posted_at: datetime | None


class JobProvider(Protocol):
    name: str

    def search(self, filt: JobSearchFilter, *, limit: int = 20) -> list[JobPosting]: ...


def _primary_term(value: str | None) -> str:
    """Take the first comma-separated entry (Adzuna takes a single query)."""
    if not value:
        return ""
    return value.split(",")[0].strip()


class MockJobProvider:
    """Deterministic sample postings derived from the filter (no network)."""

    name = "mock"

    def search(self, filt: JobSearchFilter, *, limit: int = 20) -> list[JobPosting]:
        role = _primary_term(filt.title_keywords) or "Software Engineer"
        location = _primary_term(filt.locations) or ("Remote" if filt.remote else "London")
        companies = ["Northwind", "Globex", "Initech", "Umbrella", "Hooli"]
        base_salary = filt.salary_min or 70_000
        count = min(limit, 5)
        postings: list[JobPosting] = []
        for i in range(count):
            postings.append(
                JobPosting(
                    external_id=f"mock-{role.lower().replace(' ', '-')}-{i}",
                    title=f"{role}" if i == 0 else f"{'Senior ' if i % 2 else ''}{role}",
                    company=companies[i % len(companies)],
                    location=location,
                    description=(
                        f"{companies[i % len(companies)]} is hiring a {role}. "
                        f"You'll work with a modern stack. Location: {location}."
                    ),
                    url=f"https://example.com/jobs/{role.lower().replace(' ', '-')}-{i}",
                    salary_min=base_salary + i * 5_000,
                    salary_max=base_salary + i * 5_000 + 30_000,
                    remote=filt.remote,
                    posted_at=None,
                )
            )
        return postings


class AdzunaProvider:
    """Fetches postings from the Adzuna jobs API."""

    name = "adzuna"

    def search(self, filt: JobSearchFilter, *, limit: int = 20) -> list[JobPosting]:
        import httpx  # lazy import; only needed when Adzuna is configured

        params: dict[str, str | int] = {
            "app_id": settings.adzuna_app_id or "",
            "app_key": settings.adzuna_app_key or "",
            "results_per_page": min(limit, 50),
            "content-type": "application/json",
        }
        what = _primary_term(filt.title_keywords) or _primary_term(filt.keywords)
        if what:
            params["what"] = what
        where = _primary_term(filt.locations)
        if where:
            params["where"] = where
        if filt.salary_min:
            params["salary_min"] = filt.salary_min
        if filt.salary_max:
            params["salary_max"] = filt.salary_max

        url = f"{_ADZUNA_BASE}/{settings.adzuna_country}/search/1"
        response = httpx.get(url, params=params, timeout=15.0)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [self._normalize(item) for item in results]

    @staticmethod
    def _normalize(item: dict) -> JobPosting:
        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")
        posted_raw = item.get("created")
        posted_at: datetime | None = None
        if isinstance(posted_raw, str):
            try:
                posted_at = datetime.fromisoformat(posted_raw.replace("Z", "+00:00"))
            except ValueError:
                posted_at = None
        title = str(item.get("title", "Untitled role"))
        return JobPosting(
            external_id=str(item.get("id", item.get("redirect_url", title))),
            title=title,
            company=(item.get("company") or {}).get("display_name"),
            location=(item.get("location") or {}).get("display_name"),
            description=item.get("description"),
            url=str(item.get("redirect_url", "")),
            salary_min=int(salary_min) if isinstance(salary_min, int | float) else None,
            salary_max=int(salary_max) if isinstance(salary_max, int | float) else None,
            remote="remote" in title.lower(),
            posted_at=posted_at,
        )


def get_job_provider() -> JobProvider:
    """Return the configured job provider (Adzuna when keyed, else the mock)."""
    if settings.adzuna_enabled:
        return AdzunaProvider()
    return MockJobProvider()
