"""Skill repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, func

from app.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    """Data access for :class:`Skill`."""

    model = Skill

    def list_for_user(self, owner_id: UUID) -> list[Skill]:
        stmt = self.owned_query(owner_id).order_by(asc(Skill.category), asc(Skill.name))
        return list(self.session.execute(stmt).scalars())

    def get_by_name(self, owner_id: UUID, name: str) -> Skill | None:
        stmt = self.owned_query(owner_id).where(func.lower(Skill.name) == name.lower())
        return self.session.execute(stmt).scalar_one_or_none()
