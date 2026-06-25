"""Schemas for job application resources."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.enums import ApplicationStatus
from app.schemas.base import IdentifiedModel


def _validate_salary_range(salary_min: int | None, salary_max: int | None) -> None:
    if salary_min is not None and salary_max is not None and salary_max < salary_min:
        raise ValueError("salary_max must be greater than or equal to salary_min.")


class ApplicationBase(BaseModel):
    """Fields shared by create and update payloads."""

    company_id: UUID | None = None
    role_title: str = Field(min_length=1, max_length=200)
    status: ApplicationStatus = ApplicationStatus.WISHLIST
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, min_length=3, max_length=3)
    location: str | None = Field(default=None, max_length=200)
    is_remote: bool = False
    application_url: str | None = Field(default=None, max_length=1000)
    source: str | None = Field(default=None, max_length=120)
    applied_at: datetime | None = None

    @model_validator(mode="after")
    def _check_salary(self) -> ApplicationBase:
        _validate_salary_range(self.salary_min, self.salary_max)
        return self


class ApplicationCreate(ApplicationBase):
    """Payload for creating an application."""


class ApplicationUpdate(BaseModel):
    """Payload for partially updating an application (all fields optional)."""

    company_id: UUID | None = None
    role_title: str | None = Field(default=None, min_length=1, max_length=200)
    status: ApplicationStatus | None = None
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, min_length=3, max_length=3)
    location: str | None = Field(default=None, max_length=200)
    is_remote: bool | None = None
    application_url: str | None = Field(default=None, max_length=1000)
    source: str | None = Field(default=None, max_length=120)
    applied_at: datetime | None = None

    @model_validator(mode="after")
    def _check_salary(self) -> ApplicationUpdate:
        _validate_salary_range(self.salary_min, self.salary_max)
        return self


class ApplicationRead(IdentifiedModel):
    """Application representation returned by the API."""

    company_id: UUID | None
    role_title: str
    status: ApplicationStatus
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    location: str | None
    is_remote: bool
    application_url: str | None
    source: str | None
    applied_at: datetime | None


class ApplicationImportFromUrl(BaseModel):
    """Payload for ``POST /applications/import-from-url``."""

    url: str = Field(min_length=8, max_length=1000)
    status: ApplicationStatus = ApplicationStatus.WISHLIST
    create_company: bool = True


class ApplicationImportPreview(BaseModel):
    """Fields extracted from the URL, returned alongside the created application."""

    role_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    is_remote: bool = False
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    description: str | None = None
    source: str | None = None


class ApplicationImportResult(BaseModel):
    """Result of an import: the created application plus what was extracted."""

    application: ApplicationRead
    extracted: ApplicationImportPreview
