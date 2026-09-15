"""Resolution of CV and job inputs shared by the CV-facing services.

Both CV tailoring and match scoring accept the same pair of "either/or" inputs
— a stored record by id, or text pasted inline — so the resolution lives here
rather than being written twice and drifting apart.
"""

from __future__ import annotations

from uuid import UUID

from app.core.errors import ValidationError
from app.models.user import User
from app.repositories.job import JobRepository
from app.services.cv import CvService


def resolve_cv_text(cvs: CvService, owner: User, *, cv_id: UUID | None, cv_text: str | None) -> str:
    """Return the CV text to work from, preferring inline text over a stored CV."""
    if cv_text and cv_text.strip():
        return cv_text
    # Request schemas guarantee cv_id is present when cv_text is absent; guard
    # explicitly (rather than assert) to narrow the type and stay safe.
    if cv_id is None:
        raise ValidationError("Provide either cv_id or cv_text as the base CV.")
    cv = cvs.get(owner, cv_id)
    if not cv.content_text or not cv.content_text.strip():
        raise ValidationError(
            "This CV has no extractable text. Paste the CV text directly, or "
            "use a text-based CV. (PDF/DOCX parsing isn't supported yet.)"
        )
    return cv.content_text


def resolve_job_description(
    jobs: JobRepository, owner: User, *, job_id: UUID | None, job_description: str | None
) -> str:
    """Return the job description to work from, preferring inline text."""
    if job_description and job_description.strip():
        return job_description
    if job_id is None:
        raise ValidationError("Provide either job_description or job_id.")
    job = jobs.get(owner.id, job_id)
    if job is None or not (job.description and job.description.strip()):
        raise ValidationError("That job has no description to work from.")
    return job.description
