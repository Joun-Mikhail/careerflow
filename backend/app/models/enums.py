"""Enumerations shared by models and schemas.

Using ``str``-based enums means the same values serialize cleanly to JSON, map
to native PostgreSQL enum types, and validate automatically in Pydantic.
"""

from __future__ import annotations

from enum import StrEnum


class ApplicationStatus(StrEnum):
    """Stages an application moves through in the pipeline."""

    WISHLIST = "wishlist"
    APPLIED = "applied"
    ASSESSMENT = "assessment"
    INTERVIEW = "interview"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class InterviewMode(StrEnum):
    PHONE = "phone"
    VIDEO = "video"
    ONSITE = "onsite"


class InterviewResult(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AttachmentKind(StrEnum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    OTHER = "other"


class OfferDecision(StrEnum):
    """Where the candidate stands on an offer."""

    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    DECLINED = "declined"
