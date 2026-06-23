"""Offer repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc

from app.core.pagination import PageParams
from app.models.enums import OfferDecision
from app.models.offer import Offer
from app.repositories.base import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    """Data access for :class:`Offer`."""

    model = Offer

    def list_for_application(self, owner_id: UUID, application_id: UUID) -> list[Offer]:
        stmt = (
            self.owned_query(owner_id)
            .where(Offer.application_id == application_id)
            .order_by(desc(Offer.received_at), desc(Offer.created_at))
        )
        return list(self.session.execute(stmt).scalars())

    def list_offers(
        self,
        owner_id: UUID,
        *,
        params: PageParams,
        decision: OfferDecision | None = None,
    ) -> tuple[list[Offer], int]:
        stmt = self.owned_query(owner_id)
        if decision is not None:
            stmt = stmt.where(Offer.decision == decision)
        stmt = stmt.order_by(desc(Offer.received_at), desc(Offer.created_at))
        return self.paginate(stmt, params=params)
