"""Task endpoints: CRUD plus a completion action."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Pagination
from app.core.pagination import Page
from app.models.enums import TaskPriority
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=Page[TaskRead], summary="List tasks")
def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    pagination: Pagination,
    is_completed: Annotated[bool | None, Query(description="Filter by completion.")] = None,
    priority: Annotated[TaskPriority | None, Query(description="Filter by priority.")] = None,
    sort: Literal["created_at", "due_at", "priority"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
) -> Page[TaskRead]:
    return TaskService(db).list(
        current_user,
        params=pagination,
        is_completed=is_completed,
        priority=priority,
        sort=sort,
        order=order,
    )


@router.post(
    "", response_model=TaskRead, status_code=status.HTTP_201_CREATED, summary="Create a task"
)
def create_task(data: TaskCreate, current_user: CurrentUser, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(TaskService(db).create(current_user, data))


@router.get("/{task_id}", response_model=TaskRead, summary="Get a task")
def get_task(task_id: UUID, current_user: CurrentUser, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(TaskService(db).get(current_user, task_id))


@router.patch("/{task_id}", response_model=TaskRead, summary="Update a task")
def update_task(
    task_id: UUID, data: TaskUpdate, current_user: CurrentUser, db: DbSession
) -> TaskRead:
    return TaskRead.model_validate(TaskService(db).update(current_user, task_id, data))


@router.post("/{task_id}/complete", response_model=TaskRead, summary="Mark a task complete")
def complete_task(task_id: UUID, current_user: CurrentUser, db: DbSession) -> TaskRead:
    return TaskRead.model_validate(
        TaskService(db).set_completed(current_user, task_id, completed=True)
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: UUID, current_user: CurrentUser, db: DbSession) -> None:
    TaskService(db).delete(current_user, task_id)
