from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.login import login_jwt
from app.services.logout import logout_jwt
from app.services.me import get_jwt_user
from app.services.refresh import refresh_jwt
from app.services.register import register_user
from app.shared.dependencies import get_current_user_jwt, get_db

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db=db, payload=payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="JWT Login (obtain access and refresh tokens)",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login_jwt(db=db, payload=payload)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="JWT Logout (client must discard tokens)",
)
def logout(current_user: dict = Depends(get_current_user_jwt)):
    return logout_jwt(current_user=current_user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="JWT Refresh (obtain new token pair using refresh token)",
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return refresh_jwt(db=db, payload=payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def me(current_user: dict = Depends(get_current_user_jwt)):
    return get_jwt_user(current_user=current_user)

