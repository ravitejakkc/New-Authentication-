from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.shared.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)


def login_jwt(db: Session, payload: LoginRequest) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User roles are not configured",
        )

    access_token_data = {
        "sub": user.id,
        "email": user.email,
        "roles": [role.name for role in user.roles],
    }
    refresh_token_data = {"sub": user.id}
    access_token = create_access_token(data=access_token_data)
    refresh_token = create_refresh_token(data=refresh_token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.jwt_access_token_expire_minutes,
    )
