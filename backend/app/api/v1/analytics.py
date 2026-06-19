"""Analytics endpoints providing chart-ready datasets."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import (
    ApplicationsByMonth,
    ConversionRates,
    IndustryDistribution,
    StatusDistribution,
)
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/applications-by-month",
    response_model=ApplicationsByMonth,
    summary="Applications per month (last 12 months)",
)
def applications_by_month(current_user: CurrentUser, db: DbSession) -> ApplicationsByMonth:
    return AnalyticsService(db).applications_by_month(current_user)


@router.get(
    "/status-distribution",
    response_model=StatusDistribution,
    summary="Application count per status",
)
def status_distribution(current_user: CurrentUser, db: DbSession) -> StatusDistribution:
    return AnalyticsService(db).status_distribution(current_user)


@router.get(
    "/industry-distribution",
    response_model=IndustryDistribution,
    summary="Application count per company industry",
)
def industry_distribution(current_user: CurrentUser, db: DbSession) -> IndustryDistribution:
    return AnalyticsService(db).industry_distribution(current_user)


@router.get(
    "/conversion",
    response_model=ConversionRates,
    summary="Interview and offer conversion rates",
)
def conversion(current_user: CurrentUser, db: DbSession) -> ConversionRates:
    return AnalyticsService(db).conversion(current_user)
