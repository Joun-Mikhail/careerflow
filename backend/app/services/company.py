"""Company service — business logic for managing companies."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.models.company import Company
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate


class CompanyService:
    """Coordinates company persistence and enforces ownership."""

    def __init__(self, session: Session) -> None:
        self.repo = CompanyRepository(session)

    def create(self, owner: User, data: CompanyCreate) -> Company:
        company = Company(user_id=owner.id, **data.model_dump())
        return self.repo.add(company)

    def get(self, owner: User, company_id: UUID) -> Company:
        company = self.repo.get(owner.id, company_id)
        if company is None:
            raise NotFoundError("Company not found.")
        return company

    def list(
        self,
        owner: User,
        *,
        params: PageParams,
        search: str | None = None,
        industry: str | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> Page[CompanyRead]:
        items, total = self.repo.list_companies(
            owner.id,
            params=params,
            search=search,
            industry=industry,
            sort=sort,
            order=order,
        )
        return Page.create(
            [CompanyRead.model_validate(item) for item in items],
            total=total,
            params=params,
        )

    def update(self, owner: User, company_id: UUID, data: CompanyUpdate) -> Company:
        company = self.get(owner, company_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        self.repo.flush()
        return company

    def delete(self, owner: User, company_id: UUID) -> None:
        company = self.get(owner, company_id)
        self.repo.delete(company)
