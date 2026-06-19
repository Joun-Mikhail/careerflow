"""Aggregate router for API v1.

Each feature module exposes an ``APIRouter`` mounted here under the versioned
prefix. Resources are wired in as they are implemented, phase by phase.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, companies

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(companies.router)
