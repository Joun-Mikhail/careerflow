"""CV tailoring orchestration — resolve inputs, call the AI provider, save."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logging import log_action
from app.models.user import User
from app.repositories.job import JobRepository
from app.schemas.ai import TailorCvRequest, TailorCvResponse
from app.services.ai import AiProvider, get_ai_provider
from app.services.cv import CvService
from app.services.cv_inputs import resolve_cv_text, resolve_job_description


class CvTailoringService:
    """Turns a base CV + job description into a tailored CV via an AI provider."""

    def __init__(self, session: Session, provider: AiProvider | None = None) -> None:
        self.session = session
        self.cvs = CvService(session)
        self.jobs = JobRepository(session)
        self.provider = provider or get_ai_provider()

    def tailor(self, owner: User, data: TailorCvRequest) -> TailorCvResponse:
        base_text = resolve_cv_text(self.cvs, owner, cv_id=data.cv_id, cv_text=data.cv_text)
        job_description = resolve_job_description(
            self.jobs, owner, job_id=data.job_id, job_description=data.job_description
        )

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
