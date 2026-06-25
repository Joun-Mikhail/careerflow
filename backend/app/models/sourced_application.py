"""SourcedApplication model — an application created from a fetched job.

Distinct from :class:`~app.models.application.Application` (the manual pipeline):
this tracks applications that originate from externally fetched jobs, records
which CV was used, and links to the official apply URL. CareerFlow never
auto-submits on a job board's behalf; it prepares and tracks the application
and deep-links the user to the real apply page.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import SourcedApplicationStatus

if TYPE_CHECKING:
    from app.models.job import Job
    from app.models.user import User


class SourcedApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks an application against an externally sourced job."""

    __tablename__ = "sourced_applications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # The CV used to apply; keep the record if the CV is later deleted.
    cv_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("cvs.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[SourcedApplicationStatus] = mapped_column(
        SAEnum(
            SourcedApplicationStatus,
            name="sourced_application_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=SourcedApplicationStatus.SAVED,
        nullable=False,
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    cover_letter_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship(back_populates="sourced_applications")
    job: Mapped[Job] = relationship()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<SourcedApplication id={self.id} job_id={self.job_id} status={self.status}>"
