"""Skill endpoints: list, create, update, delete."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.skill import SkillCreate, SkillRead, SkillUpdate
from app.services.skill import SkillService

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead], summary="List the current user's skills")
def list_skills(current_user: CurrentUser, db: DbSession) -> list[SkillRead]:
    return [SkillRead.model_validate(item) for item in SkillService(db).list_all(current_user)]


@router.post(
    "",
    response_model=SkillRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a skill",
)
def create_skill(data: SkillCreate, current_user: CurrentUser, db: DbSession) -> SkillRead:
    return SkillRead.model_validate(SkillService(db).create(current_user, data))


@router.patch("/{skill_id}", response_model=SkillRead, summary="Update a skill")
def update_skill(
    skill_id: UUID, data: SkillUpdate, current_user: CurrentUser, db: DbSession
) -> SkillRead:
    return SkillRead.model_validate(SkillService(db).update(current_user, skill_id, data))


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a skill")
def delete_skill(skill_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    SkillService(db).delete(current_user, skill_id)
