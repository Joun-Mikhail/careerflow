"""Task service — business logic for to-do items."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.core.pagination import Page, PageParams
from app.models.base import utcnow
from app.models.enums import TaskPriority
from app.models.task import Task
from app.models.user import User
from app.repositories.application import ApplicationRepository
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate


class TaskService:
    """Coordinates task persistence and completion semantics."""

    def __init__(self, session: Session) -> None:
        self.repo = TaskRepository(session)
        self.applications = ApplicationRepository(session)

    def create(self, owner: User, data: TaskCreate) -> Task:
        self._ensure_application_owned(owner, data.application_id)
        task = Task(user_id=owner.id, **data.model_dump())
        return self.repo.add(task)

    def get(self, owner: User, task_id: UUID) -> Task:
        task = self.repo.get(owner.id, task_id)
        if task is None:
            raise NotFoundError("Task not found.")
        return task

    def list(
        self,
        owner: User,
        *,
        params: PageParams,
        is_completed: bool | None = None,
        priority: TaskPriority | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> Page[TaskRead]:
        items, total = self.repo.list_tasks(
            owner.id,
            params=params,
            is_completed=is_completed,
            priority=priority,
            sort=sort,
            order=order,
        )
        return Page.create(
            [TaskRead.model_validate(item) for item in items], total=total, params=params
        )

    def update(self, owner: User, task_id: UUID, data: TaskUpdate) -> Task:
        task = self.get(owner, task_id)
        changes = data.model_dump(exclude_unset=True)
        if "application_id" in changes:
            self._ensure_application_owned(owner, changes["application_id"])
        if "is_completed" in changes:
            self._apply_completion(task, completed=bool(changes.pop("is_completed")))
        for field, value in changes.items():
            setattr(task, field, value)
        self.repo.flush()
        return task

    def set_completed(self, owner: User, task_id: UUID, *, completed: bool = True) -> Task:
        task = self.get(owner, task_id)
        self._apply_completion(task, completed=completed)
        self.repo.flush()
        return task

    def delete(self, owner: User, task_id: UUID) -> None:
        task = self.get(owner, task_id)
        self.repo.delete(task)

    @staticmethod
    def _apply_completion(task: Task, *, completed: bool) -> None:
        """Keep ``is_completed`` and ``completed_at`` consistent."""
        task.is_completed = completed
        task.completed_at = utcnow() if completed else None

    def _ensure_application_owned(self, owner: User, application_id: UUID | None) -> None:
        if application_id is None:
            return
        if self.applications.get(owner.id, application_id) is None:
            raise NotFoundError("Application not found.")
