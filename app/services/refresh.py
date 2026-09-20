import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenResponse
from app.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


def refresh_jwt(db: Session, payload: RefreshRequest) -> TokenResponse:
    try:
        token_data = decode_token(payload.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if token_data.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
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
    new_access_token = create_access_token(data=access_token_data)
    new_refresh_token = create_refresh_token(data=refresh_token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.jwt_access_token_expire_minutes,
    )
