"""Application service — business logic for job applications."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ValidationError, ensure_found
from app.core.logging import log_action
from app.core.pagination import Page, PageParams
from app.models.application import Application
from app.models.company import Company
from app.models.enums import ApplicationStatus
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationImportFromUrl,
    ApplicationImportPreview,
    ApplicationRead,
    ApplicationUpdate,
)
from app.services.url_import import ExtractedJob, Fetcher, extract_from_url


class ApplicationService:
    """Coordinates application persistence and cross-entity rules."""

    def __init__(self, session: Session) -> None:
        self.repo = ApplicationRepository(session)
        self.companies = CompanyRepository(session)

    def create(self, owner: User, data: ApplicationCreate) -> Application:
        self._ensure_company_owned(owner, data.company_id)
        application = Application(user_id=owner.id, **data.model_dump())
        return self.repo.add(application)

    def get(self, owner: User, application_id: UUID) -> Application:
        return ensure_found(self.repo.get(owner.id, application_id), "Application not found.")

    def list(
        self,
        owner: User,
        *,
        params: PageParams,
        search: str | None = None,
        status: ApplicationStatus | None = None,
        company_id: UUID | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> Page[ApplicationRead]:
        items, total = self.repo.list_applications(
            owner.id,
            params=params,
            search=search,
            status=status,
            company_id=company_id,
            sort=sort,
            order=order,
        )
        return Page.create(
            [ApplicationRead.model_validate(item) for item in items],
            total=total,
            params=params,
        )

    def update(self, owner: User, application_id: UUID, data: ApplicationUpdate) -> Application:
        application = self.get(owner, application_id)
        changes = data.model_dump(exclude_unset=True)
        if "company_id" in changes:
            self._ensure_company_owned(owner, changes["company_id"])
        for field, value in changes.items():
            setattr(application, field, value)
        self.repo.flush()
        return application

    def delete(self, owner: User, application_id: UUID) -> None:
        application = self.get(owner, application_id)
        self.repo.delete(application)

    def import_from_url(
        self,
        owner: User,
        data: ApplicationImportFromUrl,
        *,
        fetcher: Fetcher | None = None,
    ) -> tuple[Application, ApplicationImportPreview]:
        """Scrape ``data.url``, then create a company (optional) and application.

        Returns ``(application, preview)`` so the caller can show the user what
        was extracted and let them edit anything that the scraper got wrong.
        """
        if not data.url.lower().startswith(("http://", "https://")):
            raise ValidationError("URL must start with http:// or https://.")

        try:
            extracted = extract_from_url(data.url, fetcher=fetcher)
        except Exception as exc:
            log_action(
                "application_import_failed",
                status="error",
                user_id=owner.id,
                reason=type(exc).__name__,
            )
            raise ValidationError(
                "Could not fetch that URL — check the link and try again."
            ) from exc

        if not extracted.role_title:
            raise ValidationError(
                "We couldn't find a job title at that URL. Add the application manually."
            )

        company_id = (
            self._resolve_company(owner, extracted.company_name)
            if data.create_company and extracted.company_name
            else None
        )

        application = Application(
            user_id=owner.id,
            company_id=company_id,
            role_title=extracted.role_title,
            status=data.status,
            salary_min=extracted.salary_min,
            salary_max=extracted.salary_max,
            salary_currency=extracted.salary_currency,
            location=extracted.location,
            is_remote=extracted.is_remote,
            application_url=extracted.application_url,
            source=extracted.source,
        )
        self.repo.add(application)
        log_action(
            "application_imported",
            status="ok",
            user_id=owner.id,
            source=extracted.source,
        )
        return application, _preview_of(extracted)

    def _resolve_company(self, owner: User, name: str) -> UUID:
        """Find an existing company by case-insensitive name, or create one."""
        existing = self.companies.session.execute(
            select(Company)
            .where(Company.user_id == owner.id)
            .where(Company.deleted_at.is_(None))
            .where(Company.name.ilike(name))
        ).scalar_one_or_none()
        if existing is not None:
            return existing.id
        company = Company(user_id=owner.id, name=name)
        self.companies.add(company)
        return company.id

    def _ensure_company_owned(self, owner: User, company_id: UUID | None) -> None:
        """Validate that a referenced company exists and belongs to the user."""
        if company_id is None:
            return
        ensure_found(self.companies.get(owner.id, company_id), "Company not found.")


def _preview_of(extracted: ExtractedJob) -> ApplicationImportPreview:
    return ApplicationImportPreview(
        role_title=extracted.role_title,
        company_name=extracted.company_name,
        location=extracted.location,
        is_remote=extracted.is_remote,
        salary_min=extracted.salary_min,
        salary_max=extracted.salary_max,
        salary_currency=extracted.salary_currency,
        description=extracted.description,
        source=extracted.source,
    )
