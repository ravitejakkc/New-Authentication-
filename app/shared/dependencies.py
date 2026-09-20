from collections.abc import Generator
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.models.user import User
from app.shared.security import decode_token

security_bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_jwt(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("token_type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_role_ids(
    token_payload: dict = Depends(get_current_user_jwt),
    db: Session = Depends(get_db),
) -> list[str]:
    user_id = token_payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return [role.id for role in user.roles]
