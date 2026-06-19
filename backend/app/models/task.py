"""Task model — a to-do item, optionally tied to an application."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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
from app.models.enums import TaskPriority

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class Task(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A follow-up or preparation task in the job search."""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_user_id_is_completed", "user_id", "is_completed"),
        Index("ix_tasks_user_id_due_at", "user_id", "due_at"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("applications.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(
            TaskPriority,
            name="task_priority",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="tasks")
    application: Mapped[Application | None] = relationship()

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Task id={self.id} title={self.title!r} completed={self.is_completed}>"
