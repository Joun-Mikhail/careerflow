"""Schemas for CV-to-job match scoring."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class MatchRequest(BaseModel):
    """Request to score a CV against one or more jobs.

    Supply the CV by ``cv_id`` or by pasting ``cv_text``; ``cv_text`` wins when
    both are given. Supply the target either as ``job_ids`` (stored postings) or
    as an inline ``job_description``, or both to score them together.
    """

    cv_id: UUID | None = None
    cv_text: str | None = Field(default=None, max_length=50_000)
    job_ids: list[UUID] = Field(default_factory=list, max_length=50)
    job_description: str | None = Field(default=None, max_length=50_000)

    @model_validator(mode="after")
    def _require_inputs(self) -> MatchRequest:
        if self.cv_id is None and not (self.cv_text and self.cv_text.strip()):
            raise ValueError("Provide either cv_id or cv_text as the CV to score.")
        has_description = bool(self.job_description and self.job_description.strip())
        if not has_description and not self.job_ids:
            raise ValueError("Provide either job_ids or job_description to score against.")
        return self


class MatchBreakdownRead(BaseModel):
    """Component scores behind a match, each 0-100."""

    skills: int
    keywords: int
    seniority: int


class MatchRead(BaseModel):
    """One CV-to-job comparison.

    ``job_id`` is null for a result scored from an inline job description.
    """

    job_id: UUID | None
    score: int
    verdict: str
    matched_skills: list[str]
    missing_skills: list[str]
    missing_keywords: list[str]
    breakdown: MatchBreakdownRead
    job_seniority: str | None
    cv_seniority: str | None


class MatchResponse(BaseModel):
    """Match results, ordered strongest first."""

    results: list[MatchRead]
