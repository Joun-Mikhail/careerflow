"""Aggregate router for API v1.

Each feature module exposes an ``APIRouter`` mounted here under the versioned
prefix. Resources are wired in as they are implemented, phase by phase.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    applications,
    attachments,
    auth,
    companies,
    dashboard,
    interviews,
    notes,
    offers,
    tasks,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
api_router.include_router(applications.router)
api_router.include_router(interviews.router)
api_router.include_router(notes.router)
api_router.include_router(tasks.router)
api_router.include_router(attachments.router)
api_router.include_router(offers.router)
api_router.include_router(dashboard.router)
api_router.include_router(analytics.router)
