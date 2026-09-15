"""Interview question model — a question to prepare for, with your answer."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class InterviewQuestion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A question a user is preparing for, optionally tied to an application.

    Tags are stored as a comma-separated string rather than a join table,
    matching how saved job filters already hold their keywords. A tag here is
    a free-text label the user chose ("system design", "behavioural"), and the
    value of normalising that into its own table is small next to the cost of
    another entity to manage.
    """

    __tablename__ = "interview_questions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # Kept when the application goes away: a good answer outlives the role it
    # was first written for, which is the point of a reusable bank.
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # True once the user has actually been asked this, which separates
    # "questions I invented while prepping" from "questions that come up".
    asked: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped[User] = relationship(back_populates="interview_questions")
    application: Mapped[Application | None] = relationship(back_populates="interview_questions")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<InterviewQuestion id={self.id} question={self.question[:40]!r}>"
