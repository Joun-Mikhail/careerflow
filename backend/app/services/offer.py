"""Offer service — business logic for compensation offers."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import ensure_found
from app.core.logging import log_action
from app.core.pagination import Page, PageParams
from app.models.enums import OfferDecision
from app.models.offer import Offer
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.offer import OfferRepository
from app.schemas.offer import OfferCreate, OfferRead, OfferUpdate


class OfferService:
    """Coordinates offer persistence within an owned application."""

    def __init__(self, session: Session) -> None:
        self.repo = OfferRepository(session)
        self.applications = ApplicationRepository(session)

    def list_all(
        self,
        owner: User,
        *,
        params: PageParams,
        decision: OfferDecision | None = None,
    ) -> Page[OfferRead]:
        items, total = self.repo.list_offers(owner.id, params=params, decision=decision)
        return Page.create(
            [OfferRead.model_validate(item) for item in items], total=total, params=params
        )

    def list_for_application(self, owner: User, application_id: UUID) -> list[Offer]:
        self._ensure_application_owned(owner, application_id)
        return self.repo.list_for_application(owner.id, application_id)

    def create(self, owner: User, application_id: UUID, data: OfferCreate) -> Offer:
        self._ensure_application_owned(owner, application_id)
        offer = Offer(user_id=owner.id, application_id=application_id, **data.model_dump())
        self.repo.add(offer)
        log_action(
            "offer_decision",
            status="created",
            user_id=owner.id,
            offer_id=str(offer.id),
            decision=offer.decision.value,
        )
        return offer

    def get(self, owner: User, offer_id: UUID) -> Offer:
        return ensure_found(self.repo.get(owner.id, offer_id), "Offer not found.")

    def update(self, owner: User, offer_id: UUID, data: OfferUpdate) -> Offer:
        offer = self.get(owner, offer_id)
        changes = data.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(offer, field, value)
        self.repo.flush()
        if "decision" in changes:
            log_action(
                "offer_decision",
                status="updated",
                user_id=owner.id,
                offer_id=str(offer.id),
                decision=offer.decision.value,
            )
        return offer

    def delete(self, owner: User, offer_id: UUID) -> None:
        offer = self.get(owner, offer_id)
        self.repo.delete(offer)

    def _ensure_application_owned(self, owner: User, application_id: UUID) -> None:
        ensure_found(self.applications.get(owner.id, application_id), "Application not found.")
