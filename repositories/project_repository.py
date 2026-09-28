from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **data) -> Project:
        project = Project(**data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def find_by_id(self, project_id: int) -> Project | None:
        return self.db.get(Project, project_id)

    def find_by_owner(self, owner_id: int, skip: int = 0, limit: int = 20) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt))

    def update(self, project: Project, **data) -> Project:
        for key, value in data.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()