"""Dashboard endpoint: a single summary of the user's job search."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary, summary="Dashboard summary")
def get_summary(current_user: CurrentUser, db: DbSession) -> DashboardSummary:
    return DashboardService(db).summary(current_user)
