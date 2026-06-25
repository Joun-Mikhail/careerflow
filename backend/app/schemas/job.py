"""Schemas for job-search filters and fetched jobs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.base import IdentifiedModel


class JobSearchFilterBase(BaseModel):
    """Fields shared by filter create and update payloads."""

    name: str = Field(min_length=1, max_length=120)
    title_keywords: str | None = Field(default=None, max_length=500)
    locations: str | None = Field(default=None, max_length=500)
    keywords: str | None = Field(default=None, max_length=500)
    remote: bool = False
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    is_active: bool = True


class JobSearchFilterCreate(JobSearchFilterBase):
    """Payload for creating a job-search filter."""


class JobSearchFilterUpdate(BaseModel):
    """Payload for partially updating a filter."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    title_keywords: str | None = Field(default=None, max_length=500)
    locations: str | None = Field(default=None, max_length=500)
    keywords: str | None = Field(default=None, max_length=500)
    remote: bool | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class JobSearchFilterRead(IdentifiedModel):
    """Filter representation returned by the API."""

    name: str
    title_keywords: str | None
    locations: str | None
    keywords: str | None
    remote: bool
    salary_min: int | None
    salary_max: int | None
    is_active: bool


class JobRead(IdentifiedModel):
    """A fetched job posting returned by the API."""

    source: str
    external_id: str
    title: str
    company: str | None
    location: str | None
    description: str | None
    url: str
    salary_min: int | None
    salary_max: int | None
    remote: bool
    posted_at: datetime | None
