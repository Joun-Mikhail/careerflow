"""Skill service — CRUD for a user's skills."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ensure_found
from app.models.skill import Skill
from app.models.user import User
from app.repositories.skill import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate


class SkillService:
    """Coordinates skill persistence for the document vault."""

    def __init__(self, session: Session) -> None:
        self.repo = SkillRepository(session)

    def list_all(self, owner: User) -> list[Skill]:
        return self.repo.list_for_user(owner.id)

    def create(self, owner: User, data: SkillCreate) -> Skill:
        if self.repo.get_by_name(owner.id, data.name) is not None:
            raise ConflictError(f"You already have a skill named {data.name!r}.")
        skill = Skill(user_id=owner.id, **data.model_dump())
        return self.repo.add(skill)

    def get(self, owner: User, skill_id: UUID) -> Skill:
        return ensure_found(self.repo.get(owner.id, skill_id), "Skill not found.")

    def update(self, owner: User, skill_id: UUID, data: SkillUpdate) -> Skill:
        skill = self.get(owner, skill_id)
        changes = data.model_dump(exclude_unset=True)
        new_name = changes.get("name")
        if new_name and new_name.lower() != skill.name.lower():
            existing = self.repo.get_by_name(owner.id, new_name)
            if existing is not None and existing.id != skill.id:
                raise ConflictError(f"You already have a skill named {new_name!r}.")
        for field, value in changes.items():
            setattr(skill, field, value)
        self.repo.flush()
        return skill

    def delete(self, owner: User, skill_id: UUID) -> None:
        self.repo.delete(self.get(owner, skill_id))
