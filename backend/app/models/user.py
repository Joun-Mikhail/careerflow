"""User account model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.automation_rule import AutomationRule
    from app.models.certificate import Certificate
    from app.models.company import Company
    from app.models.cv import Cv
    from app.models.job import Job
    from app.models.job_search_filter import JobSearchFilter
    from app.models.skill import Skill
    from app.models.sourced_application import SourcedApplication
    from app.models.task import Task


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An authenticated CareerFlow user and owner of all their data."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    companies: Mapped[list[Company]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[list[Application]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    tasks: Mapped[list[Task]] = relationship(back_populates="user", cascade="all, delete-orphan")

    # Smart job-search feature.
    cvs: Mapped[list[Cv]] = relationship(back_populates="user", cascade="all, delete-orphan")
    certificates: Mapped[list[Certificate]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[list[Skill]] = relationship(back_populates="user", cascade="all, delete-orphan")
    job_search_filters: Mapped[list[JobSearchFilter]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[Job]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sourced_applications: Mapped[list[SourcedApplication]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    automation_rules: Mapped[list[AutomationRule]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id} email={self.email!r}>"
