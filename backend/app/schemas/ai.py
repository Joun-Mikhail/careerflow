"""Schemas for AI CV-tailoring endpoints."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class TailorCvRequest(BaseModel):
    """Request to tailor a CV to a job description.

    Provide the base CV either by ``cv_id`` (uses its stored text) or by
    pasting ``cv_text`` directly. ``cv_text`` wins when both are given.
    """

    cv_id: UUID | None = None
    cv_text: str | None = Field(default=None, max_length=50_000)
    job_description: str = Field(min_length=20, max_length=50_000)
    include_cover_letter: bool = False
    # When set, the tailored result is saved as a new CV with this title.
    save_as_title: str | None = Field(default=None, min_length=1, max_length=200)

    @model_validator(mode="after")
    def _require_a_base(self) -> TailorCvRequest:
        if self.cv_id is None and not (self.cv_text and self.cv_text.strip()):
            raise ValueError("Provide either cv_id or cv_text as the base CV.")
        return self


class TailorCvResponse(BaseModel):
    """The tailored CV and optional cover letter."""

    tailored_cv: str
    cover_letter: str | None
    provider: str
    saved_cv_id: UUID | None
