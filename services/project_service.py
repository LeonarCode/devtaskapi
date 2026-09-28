from sqlalchemy.orm import Session

from models import Project, User
from models.enum import UserRoles
from repositories.project_repository import ProjectRepository
from schemas.project_schema import ProjectCreate, ProjectUpdate
from utils.exceptions import ProjectNotFoundError


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create(self, data: ProjectCreate, user: User) -> Project:
        return self.repo.create(**data.model_dump(), owner_id=user.id)

    def list_for_user(self, user: User, skip: int = 0, limit: int = 20) -> list[Project]:
        return self.repo.find_by_owner(user.id, skip, limit)

    def get_owned(self, project_id: int, user: User) -> Project:
        project = self.repo.find_by_id(project_id)
        is_admin = user.roles == UserRoles.ADMIN
        if not project or (project.owner_id != user.id and not is_admin):
            raise ProjectNotFoundError()
        return project

    def update(self, project_id: int, data: ProjectUpdate, user: User) -> Project:
        project = self.get_owned(project_id, user)
        return self.repo.update(project, **data.model_dump(exclude_unset=True))

    def delete(self, project_id: int, user: User) -> None:
        project = self.get_owned(project_id, user)
        self.repo.delete(project)