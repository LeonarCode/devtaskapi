from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from models import Task
from models.enum import TaskPriority, TaskStatus


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **data) -> Task:
        task = Task(**data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def find_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def _apply_filters(
        self,
        stmt: Select,
        status: TaskStatus | None,
        priority: TaskPriority | None,
    ) -> Select:
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        return stmt

    def find_by_project(
        self,
        project_id: int,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assigned_to: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        stmt = select(Task).where(Task.project_id == project_id)
        stmt = self._apply_filters(stmt, status, priority)
        if assigned_to is not None:
            stmt = stmt.where(Task.assigned_to == assigned_to)
        stmt = (
            stmt.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def find_by_assignee(
        self,
        user_id: int,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        stmt = select(Task).where(Task.assigned_to == user_id)
        stmt = self._apply_filters(stmt, status, priority)
        stmt = (
            stmt.order_by(Task.due_date.asc().nulls_last(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def update(self, task: Task, **data) -> Task:
        for key, value in data.items():
            setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()