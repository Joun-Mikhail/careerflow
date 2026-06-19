"""Company endpoints: CRUD with search, filtering, sorting, and pagination."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Pagination
from app.core.pagination import Page
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.company import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=Page[CompanyRead], summary="List companies")
def list_companies(
    current_user: CurrentUser,
    db: DbSession,
    pagination: Pagination,
    q: Annotated[str | None, Query(description="Search by company name.")] = None,
    industry: Annotated[str | None, Query(description="Filter by exact industry.")] = None,
    sort: Literal["created_at", "updated_at", "name"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[CompanyRead]:
    return CompanyService(db).list(
        current_user,
        params=pagination,
        search=q,
        industry=industry,
        sort=sort,
        order=order,
    )


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a company",
)
def create_company(
    data: CompanyCreate, current_user: CurrentUser, db: DbSession
) -> CompanyRead:
    company = CompanyService(db).create(current_user, data)
    return CompanyRead.model_validate(company)


@router.get("/{company_id}", response_model=CompanyRead, summary="Get a company")
def get_company(
    company_id: UUID, current_user: CurrentUser, db: DbSession
) -> CompanyRead:
    return CompanyRead.model_validate(CompanyService(db).get(current_user, company_id))


@router.patch("/{company_id}", response_model=CompanyRead, summary="Update a company")
def update_company(
    company_id: UUID, data: CompanyUpdate, current_user: CurrentUser, db: DbSession
) -> CompanyRead:
    company = CompanyService(db).update(current_user, company_id, data)
    return CompanyRead.model_validate(company)


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a company (soft delete)",
)
def delete_company(company_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    CompanyService(db).delete(current_user, company_id)
