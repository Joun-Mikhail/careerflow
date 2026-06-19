"""Interview model — a scheduled conversation tied to an application."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import InterviewMode, InterviewResult

if TYPE_CHECKING:
    from app.models.application import Application


class Interview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single interview round for an application."""

    __tablename__ = "interviews"
    __table_args__ = (Index("ix_interviews_user_id_scheduled_at", "user_id", "scheduled_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    round_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    interviewer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    mode: Mapped[InterviewMode] = mapped_column(
        SAEnum(
            InterviewMode,
            name="interview_mode",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=InterviewMode.VIDEO,
        nullable=False,
    )
    result: Mapped[InterviewResult] = mapped_column(
        SAEnum(
            InterviewResult,
            name="interview_result",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=InterviewResult.PENDING,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped[Application] = relationship(back_populates="interviews")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Interview id={self.id} scheduled_at={self.scheduled_at} result={self.result}>"
