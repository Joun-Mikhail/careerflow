"""Skill model — a single skill/competency on a user's profile."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import SkillProficiency

if TYPE_CHECKING:
    from app.models.user import User


class Skill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A skill a user lists, with an optional category and proficiency."""

    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_skill_user_name"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    proficiency: Mapped[SkillProficiency | None] = mapped_column(
        SAEnum(
            SkillProficiency,
            name="skill_proficiency",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=True,
    )

    user: Mapped[User] = relationship(back_populates="skills")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Skill id={self.id} name={self.name!r}>"
