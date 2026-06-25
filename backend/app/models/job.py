"""Job model — a job posting fetched from an external source."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A normalized job posting fetched for a user from an external source.

    Jobs are scoped to the user who fetched them and deduplicated per source
    via ``(user_id, source, external_id)``.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "source", "external_id", name="uq_job_user_source_external"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    source: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="jobs")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Job id={self.id} title={self.title!r} source={self.source}>"
