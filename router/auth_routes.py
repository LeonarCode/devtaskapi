from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from utils.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from utils.auth_dependency import get_current_user, get_user_service
from models import User
from schemas.token_schema import Token
from schemas.user_schema import UserCreate, UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, service: AuthService = Depends(get_user_service)):
    try:
        return service.register(data)
    except EmailAlreadyExistsError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_user_service),
):
    # form.username ang email (OAuth2 standard na "username" ang pangalan ng field)
    try:
        token = service.login(form.username, form.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user