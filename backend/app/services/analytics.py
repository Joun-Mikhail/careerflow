"""Analytics service — derives chart datasets from aggregate stats."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.enums import ApplicationStatus
from app.models.user import User
from app.repositories.stats import StatsRepository
from app.schemas.analytics import (
    ApplicationsByMonth,
    ConversionRates,
    IndustryCount,
    IndustryDistribution,
    MonthCount,
    StatusCount,
    StatusDistribution,
)

MONTHS_WINDOW = 12


def _month_key(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def _recent_month_keys(now: datetime, count: int) -> list[str]:
    """Return the last ``count`` month keys, oldest first, ending at ``now``."""
    year, month = now.year, now.month
    keys: list[str] = []
    for _ in range(count):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(keys))


class AnalyticsService:
    """Computes the analytics datasets for a user."""

    def __init__(self, session: Session, *, now: datetime | None = None) -> None:
        self.stats = StatsRepository(session)
        self._now = now or datetime.now(UTC)

    def applications_by_month(self, owner: User) -> ApplicationsByMonth:
        month_keys = _recent_month_keys(self._now, MONTHS_WINDOW)
        buckets = dict.fromkeys(month_keys, 0)
        # Anchor the window at the first day of the oldest month.
        oldest = datetime(int(month_keys[0][:4]), int(month_keys[0][5:]), 1, tzinfo=UTC)
        for date in self.stats.application_dates(owner.id, since=oldest):
            key = _month_key(date)
            if key in buckets:
                buckets[key] += 1
        return ApplicationsByMonth(
            items=[MonthCount(month=key, count=buckets[key]) for key in month_keys]
        )

    def status_distribution(self, owner: User) -> StatusDistribution:
        distribution = self.stats.status_distribution(owner.id)
        return StatusDistribution(
            items=[
                StatusCount(status=status.value, count=distribution[status])
                for status in ApplicationStatus
            ]
        )

    def industry_distribution(self, owner: User) -> IndustryDistribution:
        distribution = self.stats.industry_distribution(owner.id)
        items = [
            IndustryCount(industry=industry, count=count)
            for industry, count in sorted(
                distribution.items(), key=lambda pair: pair[1], reverse=True
            )
        ]
        return IndustryDistribution(items=items)

    def conversion(self, owner: User) -> ConversionRates:
        distribution = self.stats.status_distribution(owner.id)
        total = sum(distribution.values())
        with_interviews = self.stats.count_applications_with_interviews(owner.id)
        successes = distribution[ApplicationStatus.OFFER] + distribution[ApplicationStatus.ACCEPTED]
        return ConversionRates(
            total_applications=total,
            interview_rate=round(with_interviews / total * 100, 1) if total else 0.0,
            offer_rate=round(successes / total * 100, 1) if total else 0.0,
        )
