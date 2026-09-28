# repositories/user_repository.py
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, **data) -> User:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def find_user_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def find_user_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)