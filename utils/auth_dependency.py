from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config.database import get_db
from utils.exceptions import UserNotFoundError
from utils.security import decode_access_token
from models import User
from models.enum import UserRoles
from services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_user_service),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized

    try:
        user = service.get_user(user_id)
    except UserNotFoundError:
        raise unauthorized

    if not user.is_active:
        raise unauthorized

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.roles != UserRoles.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return current_user