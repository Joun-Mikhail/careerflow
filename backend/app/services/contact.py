"""Contact service — CRUD for a user's recruiters and hiring managers."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.models.contact import Contact
from app.models.user import User
from app.repositories.company import CompanyRepository
from app.repositories.contact import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    """Coordinates contact persistence and their link to companies."""

    def __init__(self, session: Session) -> None:
        self.repo = ContactRepository(session)
        self.companies = CompanyRepository(session)

    def list_all(
        self,
        owner: User,
        *,
        search: str | None = None,
        company_id: UUID | None = None,
    ) -> list[Contact]:
        return self.repo.list_for_user(owner.id, search=search, company_id=company_id)

    def create(self, owner: User, data: ContactCreate) -> Contact:
        self._ensure_company_owned(owner, data.company_id)
        contact = Contact(user_id=owner.id, **_as_columns(data.model_dump()))
        return self.repo.add(contact)

    def get(self, owner: User, contact_id: UUID) -> Contact:
        return ensure_found(self.repo.get(owner.id, contact_id), "Contact not found.")

    def update(self, owner: User, contact_id: UUID, data: ContactUpdate) -> Contact:
        contact = self.get(owner, contact_id)
        changes = _as_columns(data.model_dump(exclude_unset=True))
        # Read the id off the validated schema, not the widened dict, so the
        # ownership check keeps its type.
        if "company_id" in changes:
            self._ensure_company_owned(owner, data.company_id)
        for field, value in changes.items():
            setattr(contact, field, value)
        self.repo.flush()
        return contact

    def delete(self, owner: User, contact_id: UUID) -> None:
        self.repo.delete(self.get(owner, contact_id))

    def _ensure_company_owned(self, owner: User, company_id: UUID | None) -> None:
        """Validate that a referenced company exists and belongs to the user."""
        if company_id is None:
            return
        ensure_found(self.companies.get(owner.id, company_id), "Company not found.")


def _as_columns(changes: dict[str, object]) -> dict[str, object]:
    """Convert validated values into what the column expects.

    ``EmailStr`` is its own type; the column stores a plain string.
    """
    if changes.get("email") is not None:
        changes["email"] = str(changes["email"])
    return changes
