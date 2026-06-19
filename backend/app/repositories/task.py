"""Task repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import asc, case, desc

from app.core.pagination import PageParams
from app.models.enums import TaskPriority
from app.models.task import Task
from app.repositories.base import BaseRepository

# Semantic ordering for priority (high first when descending) rather than the
# alphabetical order of the stored string values.
_PRIORITY_RANK = case(
    {TaskPriority.LOW: 0, TaskPriority.MEDIUM: 1, TaskPriority.HIGH: 2},
    value=Task.priority,
)

SORTABLE_FIELDS = {
    "created_at": Task.created_at,
    "due_at": Task.due_at,
    "priority": _PRIORITY_RANK,
}


class TaskRepository(BaseRepository[Task]):
    """Data access for :class:`Task`."""

    model = Task

    def list_tasks(
        self,
        owner_id: UUID,
        *,
        params: PageParams,
        is_completed: bool | None = None,
        priority: TaskPriority | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> tuple[list[Task], int]:
        stmt = self.owned_query(owner_id)
        if is_completed is not None:
            stmt = stmt.where(Task.is_completed == is_completed)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)

        column = SORTABLE_FIELDS.get(sort, Task.created_at)
        direction = asc if order == "asc" else desc
        stmt = stmt.order_by(direction(column), desc(Task.id))
        return self.paginate(stmt, params=params)
