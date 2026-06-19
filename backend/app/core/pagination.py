"""Reusable pagination primitives shared by all list endpoints.

The :class:`PageParams` dependency captures the common ``page``/``page_size``
query parameters, and :class:`Page` is the generic response envelope documented
in ``docs/04-api-design.md``.
"""

from __future__ import annotations

from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

MAX_PAGE_SIZE = 100


class PageParams(BaseModel):
    """Common pagination query parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class Page(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], *, total: int, params: PageParams) -> Page[T]:
        total_pages = ceil(total / params.page_size) if params.page_size else 0
        return cls(
            items=items,
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
        )
