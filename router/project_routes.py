from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.database import get_db
from models import User
from schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from services.project_service import ProjectService
from utils.auth_dependency import get_current_user
from utils.exceptions import ProjectNotFoundError

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.create(data, user)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    return service.list_for_user(user, skip, limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        return service.get_owned(project_id, user)
    except ProjectNotFoundError:
        raise NOT_FOUND


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        return service.update(project_id, data, user)
    except ProjectNotFoundError:
        raise NOT_FOUND


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
):
    try:
        service.delete(project_id, user)
    except ProjectNotFoundError:
        raise NOT_FOUND