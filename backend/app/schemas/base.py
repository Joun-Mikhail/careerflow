"""Base Pydantic schemas shared across the API."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for response schemas read from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class IdentifiedModel(ORMModel):
    """Response base carrying identity and audit timestamps."""

    id: UUID
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Generic message envelope for simple acknowledgements."""

    message: str
