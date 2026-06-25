"""SQLAlchemy ORM models.

Importing this package registers every model on the shared declarative
``Base.metadata``, which Alembic and the test fixtures rely on to create the
schema. Import order matters only in that all models must be imported before
``Base.metadata`` is used.
"""

from __future__ import annotations

from app.models.application import Application
from app.models.attachment import Attachment
from app.models.automation_rule import AutomationRule
from app.models.certificate import Certificate
from app.models.company import Company
from app.models.cv import Cv
from app.models.enums import (
    ApplicationStatus,
    AttachmentKind,
    CvSource,
    InterviewMode,
    InterviewResult,
    OfferDecision,
    RunFrequency,
    SkillProficiency,
    SourcedApplicationStatus,
    TaskPriority,
)
from app.models.interview import Interview
from app.models.job import Job
from app.models.job_search_filter import JobSearchFilter
from app.models.note import Note
from app.models.offer import Offer
from app.models.skill import Skill
from app.models.sourced_application import SourcedApplication
from app.models.task import Task
from app.models.user import User

__all__ = [
    "Application",
    "ApplicationStatus",
    "Attachment",
    "AttachmentKind",
    "AutomationRule",
    "Certificate",
    "Company",
    "Cv",
    "CvSource",
    "Interview",
    "InterviewMode",
    "InterviewResult",
    "Job",
    "JobSearchFilter",
    "Note",
    "Offer",
    "OfferDecision",
    "RunFrequency",
    "Skill",
    "SkillProficiency",
    "SourcedApplication",
    "SourcedApplicationStatus",
    "Task",
    "TaskPriority",
    "User",
]
