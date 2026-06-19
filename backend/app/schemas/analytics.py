"""Schemas for analytics datasets (shaped for charting)."""

from __future__ import annotations

from pydantic import BaseModel


class MonthCount(BaseModel):
    """Applications created/applied in a given month."""

    month: str  # "YYYY-MM"
    count: int


class StatusCount(BaseModel):
    """Count of applications in a given status."""

    status: str
    count: int


class IndustryCount(BaseModel):
    """Count of applications grouped by company industry."""

    industry: str
    count: int


class ApplicationsByMonth(BaseModel):
    """Time series of applications over the last twelve months."""

    items: list[MonthCount]


class StatusDistribution(BaseModel):
    items: list[StatusCount]


class IndustryDistribution(BaseModel):
    items: list[IndustryCount]


class ConversionRates(BaseModel):
    """Funnel conversion metrics, expressed as percentages."""

    total_applications: int
    interview_rate: float
    offer_rate: float
