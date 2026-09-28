from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from models import User
from models.enum import TaskPriority, TaskStatus
from schemas.task_schema import (
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from services.task_service import TaskService
from utils.auth_dependency import get_current_user

router = APIRouter(tags=["tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)


# ---------- nested sa project (owner / admin) ----------

@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    data: TaskCreate,
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.create(project_id, data, user)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
def list_project_tasks(
    project_id: int,
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = None,
    assigned_to: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.list_for_project(
        project_id,
        user,
        status=status_filter,
        priority=priority,
        assigned_to=assigned_to,
        skip=skip,
        limit=limit,
    )


@router.get("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    project_id: int,
    task_id: int,
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.get(project_id, task_id, user)


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.update(project_id, task_id, data, user)


@router.delete(
    "/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    project_id: int,
    task_id: int,
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    service.delete(project_id, task_id, user)


# ---------- para sa assignee ----------

@router.get("/tasks/assigned", response_model=list[TaskResponse])
def my_assigned_tasks(
    status_filter: TaskStatus | None = Query(None, alias="status"),
    priority: TaskPriority | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.list_assigned(
        user, status=status_filter, priority=priority, skip=skip, limit=limit
    )


@router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
def update_my_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
):
    return service.update_status(task_id, data.status, user)