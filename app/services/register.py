from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.authorization import get_role_or_404, seed_authorization_defaults
from app.models.role import RoleName
from app.shared.security import hash_password


def register_user(db: Session, payload: RegisterRequest) -> UserResponse:
    seed_authorization_defaults(db)
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=get_role_or_404(db, RoleName.MEMBER),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.name,
    )
