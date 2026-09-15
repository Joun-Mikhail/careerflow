"""Match-scoring orchestration — resolve inputs, score, rank."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.core.logging import log_action
from app.models.user import User
from app.repositories.job import JobRepository
from app.schemas.matching import (
    MatchBreakdownRead,
    MatchRead,
    MatchRequest,
    MatchResponse,
)
from app.services.cv import CvService
from app.services.cv_inputs import resolve_cv_text
from app.services.matching import MatchResult, score_match


class MatchScoringService:
    """Scores one CV against stored jobs and/or an inline job description."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.cvs = CvService(session)
        self.jobs = JobRepository(session)

    def score(self, owner: User, data: MatchRequest) -> MatchResponse:
        cv_text = resolve_cv_text(self.cvs, owner, cv_id=data.cv_id, cv_text=data.cv_text)

        results: list[MatchRead] = []

        for job_id in data.job_ids:
            job = self.jobs.get(owner.id, job_id)
            # Skip rather than fail the batch: one stale id should not cost the
            # user every other score they asked for.
            if job is None or not (job.description and job.description.strip()):
                continue
            results.append(
                _to_read(score_match(cv_text=cv_text, job_description=job.description), job_id)
            )

        if data.job_description and data.job_description.strip():
            results.append(
                _to_read(score_match(cv_text=cv_text, job_description=data.job_description), None)
            )

        if not results:
            raise ValidationError("None of those jobs have a description to score against.")

        results.sort(key=lambda match: match.score, reverse=True)

        log_action(
            "cv_match_scored",
            status="scored",
            user_id=owner.id,
            jobs=len(results),
        )
        return MatchResponse(results=results)


def _to_read(result: MatchResult, job_id: UUID | None) -> MatchRead:
    return MatchRead(
        job_id=job_id,
        score=result.score,
        verdict=result.verdict,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        missing_keywords=result.missing_keywords,
        breakdown=MatchBreakdownRead(
            skills=result.breakdown.skills,
            keywords=result.breakdown.keywords,
            seniority=result.breakdown.seniority,
        ),
        job_seniority=result.job_seniority,
        cv_seniority=result.cv_seniority,
    )
