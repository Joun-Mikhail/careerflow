"""Offer endpoints: a global list plus per-application and direct addressing."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Pagination
from app.core.pagination import Page
from app.models.enums import OfferDecision
from app.schemas.offer import OfferCreate, OfferRead, OfferUpdate
from app.services.offer import OfferService

router = APIRouter(tags=["offers"])


@router.get("/offers", response_model=Page[OfferRead], summary="List all offers")
def list_offers(
    current_user: CurrentUser,
    db: DbSession,
    pagination: Pagination,
    decision: Annotated[OfferDecision | None, Query(description="Filter by decision.")] = None,
) -> Page[OfferRead]:
    return OfferService(db).list_all(current_user, params=pagination, decision=decision)


@router.get(
    "/applications/{application_id}/offers",
    response_model=list[OfferRead],
    summary="List offers for an application",
)
def list_for_application(
    application_id: UUID, current_user: CurrentUser, db: DbSession
) -> list[OfferRead]:
    offers = OfferService(db).list_for_application(current_user, application_id)
    return [OfferRead.model_validate(item) for item in offers]


@router.post(
    "/applications/{application_id}/offers",
    response_model=OfferRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an offer for an application",
)
def create_offer(
    application_id: UUID, data: OfferCreate, current_user: CurrentUser, db: DbSession
) -> OfferRead:
    offer = OfferService(db).create(current_user, application_id, data)
    return OfferRead.model_validate(offer)


@router.get("/offers/{offer_id}", response_model=OfferRead, summary="Get an offer")
def get_offer(offer_id: UUID, current_user: CurrentUser, db: DbSession) -> OfferRead:
    return OfferRead.model_validate(OfferService(db).get(current_user, offer_id))


@router.patch("/offers/{offer_id}", response_model=OfferRead, summary="Update an offer")
def update_offer(
    offer_id: UUID, data: OfferUpdate, current_user: CurrentUser, db: DbSession
) -> OfferRead:
    return OfferRead.model_validate(OfferService(db).update(current_user, offer_id, data))


@router.delete(
    "/offers/{offer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an offer"
)
def delete_offer(offer_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    OfferService(db).delete(current_user, offer_id)
