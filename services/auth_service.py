from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from utils.exceptions import (
    EmailAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
)
from utils.security import hash_password, verify_password, create_access_token
from models import User
from schemas.user_schema import UserCreate

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.repo.find_user_by_email(data.email):
            raise EmailAlreadyExistsError()

        return self.repo.create_user(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
        )

    def authenticate(self, email: str, password: str) -> User:
        user = self.repo.find_user_by_email(email)

        # parehong error para hindi malaman kung existing ang email
        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()

        return user

    def login(self, email: str, password: str) -> str:
        user = self.authenticate(email, password)
        return create_access_token(user.id)

    def get_user(self, user_id: int) -> User:
        user = self.repo.find_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user