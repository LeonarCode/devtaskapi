from sqlalchemy.orm import Session

from models import Task, User
from models.enum import TaskPriority, TaskStatus, UserRoles
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from schemas.task_schema import TaskCreate, TaskUpdate
from services.project_service import ProjectService
from utils.exceptions import InvalidAssigneeError, TaskNotFoundError

# Ito lang ang pwedeng gawing null. Ang iba ay hindi nullable sa DB.
NULLABLE_FIELDS = {"assigned_to", "due_date"}


class TaskService:
    def __init__(self, db: Session):
        self.repo = TaskRepository(db)
        self.projects = ProjectService(db)
        self.users = UserRepository(db)

    def _validate_assignee(self, user_id: int) -> None:
        user = self.users.find_user_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidAssigneeError()

    # --- owner / admin ---

    def create(self, project_id: int, data: TaskCreate, user: User) -> Task:
        self.projects.get_owned(project_id, user)  # raises ProjectNotFoundError
        if data.assigned_to is not None:
            self._validate_assignee(data.assigned_to)
        return self.repo.create(**data.model_dump(), project_id=project_id)

    def list_for_project(
        self,
        project_id: int,
        user: User,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assigned_to: int | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        self.projects.get_owned(project_id, user)
        return self.repo.find_by_project(
            project_id,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            skip=skip,
            limit=limit,
        )

    def get(self, project_id: int, task_id: int, user: User) -> Task:
        self.projects.get_owned(project_id, user)
        task = self.repo.find_by_id(task_id)
        # kailangang nasa parehong project, kung hindi ay 404
        if not task or task.project_id != project_id:
            raise TaskNotFoundError()
        return task

    def update(
        self, project_id: int, task_id: int, data: TaskUpdate, user: User
    ) -> Task:
        task = self.get(project_id, task_id, user)
        changes = {
            k: v
            for k, v in data.model_dump(exclude_unset=True).items()
            if v is not None or k in NULLABLE_FIELDS
        }
        if changes.get("assigned_to") is not None:
            self._validate_assignee(changes["assigned_to"])
        return self.repo.update(task, **changes)

    def delete(self, project_id: int, task_id: int, user: User) -> None:
        task = self.get(project_id, task_id, user)
        self.repo.delete(task)

    # --- assignee ---

    def list_assigned(
        self,
        user: User,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Task]:
        return self.repo.find_by_assignee(
            user.id, status=status, priority=priority, skip=skip, limit=limit
        )

    def update_status(self, task_id: int, status: TaskStatus, user: User) -> Task:
        task = self.repo.find_by_id(task_id)
        is_admin = user.roles == UserRoles.ADMIN
        if not task or (task.assigned_to != user.id and not is_admin):
            raise TaskNotFoundError()
        return self.repo.update(task, status=status)