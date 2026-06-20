"""Application service — business logic for job applications."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.core.pagination import Page, PageParams
from app.models.application import Application
from app.models.enums import ApplicationStatus
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.company import CompanyRepository
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate


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

    def _ensure_company_owned(self, owner: User, company_id: UUID | None) -> None:
        """Validate that a referenced company exists and belongs to the user."""
        if company_id is None:
            return
        ensure_found(self.companies.get(owner.id, company_id), "Company not found.")
