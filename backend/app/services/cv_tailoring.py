"""CV tailoring orchestration — resolve inputs, call the AI provider, save."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.core.logging import log_action
from app.models.user import User
from app.repositories.job import JobRepository
from app.schemas.ai import TailorCvRequest, TailorCvResponse
from app.services.ai import AiProvider, get_ai_provider
from app.services.cv import CvService


class CvTailoringService:
    """Turns a base CV + job description into a tailored CV via an AI provider."""

    def __init__(self, session: Session, provider: AiProvider | None = None) -> None:
        self.session = session
        self.cvs = CvService(session)
        self.jobs = JobRepository(session)
        self.provider = provider or get_ai_provider()

    def tailor(self, owner: User, data: TailorCvRequest) -> TailorCvResponse:
        base_text = self._resolve_base_text(owner, data)
        job_description = self._resolve_job_description(owner, data)

        result = self.provider.tailor_cv(
            cv_text=base_text,
            job_description=job_description,
            include_cover_letter=data.include_cover_letter,
        )

        saved_cv_id = None
        if data.save_as_title:
            cv = self.cvs.save_tailored(
                owner,
                title=data.save_as_title,
                content_text=result.tailored_cv,
                parent_cv_id=data.cv_id,
                job_id=data.job_id,
            )
            saved_cv_id = cv.id

        log_action(
            "cv_tailored",
            status="generated",
            user_id=owner.id,
            provider=result.provider,
            saved=bool(saved_cv_id),
        )
        return TailorCvResponse(
            tailored_cv=result.tailored_cv,
            cover_letter=result.cover_letter,
            provider=result.provider,
            saved_cv_id=saved_cv_id,
        )

    def _resolve_base_text(self, owner: User, data: TailorCvRequest) -> str:
        if data.cv_text and data.cv_text.strip():
            return data.cv_text
        # The schema guarantees cv_id is present when cv_text is absent; guard
        # explicitly (rather than assert) to narrow the type and stay safe.
        if data.cv_id is None:
            raise ValidationError("Provide either cv_id or cv_text as the base CV.")
        cv = self.cvs.get(owner, data.cv_id)
        if not cv.content_text or not cv.content_text.strip():
            raise ValidationError(
                "This CV has no extractable text. Paste the CV text directly, or "
                "tailor from a text-based CV. (PDF/DOCX parsing isn't supported yet.)"
            )
        return cv.content_text

    def _resolve_job_description(self, owner: User, data: TailorCvRequest) -> str:
        if data.job_description and data.job_description.strip():
            return data.job_description
        # job_id is guaranteed present by the schema validator otherwise.
        if data.job_id is None:
            raise ValidationError("Provide either job_description or job_id.")
        job = self.jobs.get(owner.id, data.job_id)
        if job is None or not (job.description and job.description.strip()):
            raise ValidationError("That job has no description to tailor against.")
        return job.description
