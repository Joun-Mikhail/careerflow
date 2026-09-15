"""Contact endpoints: list, create, update, delete."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "",
    response_model=list[ContactRead],
    summary="List contacts, optionally searched or filtered by company",
)
def list_contacts(
    current_user: CurrentUser,
    db: DbSession,
    search: str | None = Query(default=None, max_length=200),
    company_id: UUID | None = None,
) -> list[ContactRead]:
    contacts = ContactService(db).list_all(current_user, search=search, company_id=company_id)
    return [ContactRead.model_validate(item) for item in contacts]


@router.post(
    "",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a contact",
)
def create_contact(data: ContactCreate, current_user: CurrentUser, db: DbSession) -> ContactRead:
    return ContactRead.model_validate(ContactService(db).create(current_user, data))


@router.patch("/{contact_id}", response_model=ContactRead, summary="Update a contact")
def update_contact(
    contact_id: UUID, data: ContactUpdate, current_user: CurrentUser, db: DbSession
) -> ContactRead:
    return ContactRead.model_validate(ContactService(db).update(current_user, contact_id, data))


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a contact",
)
def delete_contact(contact_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    ContactService(db).delete(current_user, contact_id)
