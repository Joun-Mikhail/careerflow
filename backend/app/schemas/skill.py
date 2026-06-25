"""Schemas for skill resources."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import SkillProficiency
from app.schemas.base import IdentifiedModel


class SkillCreate(BaseModel):
    """Payload for adding a skill."""

    name: str = Field(min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=80)
    proficiency: SkillProficiency | None = None


class SkillUpdate(BaseModel):
    """Payload for partially updating a skill."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=80)
    proficiency: SkillProficiency | None = None


class SkillRead(IdentifiedModel):
    """Skill representation returned by the API."""

    name: str
    category: str | None
    proficiency: SkillProficiency | None
