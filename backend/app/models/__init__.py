"""SQLAlchemy ORM models.

Importing this package registers every model on the shared declarative
``Base.metadata``, which Alembic and the test fixtures rely on to create the
schema. Import order matters only in that all models must be imported before
``Base.metadata`` is used.
"""

from __future__ import annotations

from app.models.application import Application
from app.models.attachment import Attachment
from app.models.company import Company
from app.models.enums import (
    ApplicationStatus,
    AttachmentKind,
    InterviewMode,
    InterviewResult,
    TaskPriority,
)
from app.models.interview import Interview
from app.models.note import Note
from app.models.task import Task
from app.models.user import User

__all__ = [
    "Application",
    "ApplicationStatus",
    "Attachment",
    "AttachmentKind",
    "Company",
    "Interview",
    "InterviewMode",
    "InterviewResult",
    "Note",
    "Task",
    "TaskPriority",
    "User",
]
