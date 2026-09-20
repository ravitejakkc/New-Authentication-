from collections.abc import Callable
from pathlib import Path

import casbin
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User
from app.shared.dependencies import get_current_user_jwt, get_db

CASBIN_MODEL_PATH = Path(__file__).with_name("model.config")


def _build_enforcer(user: User) -> casbin.Enforcer:
    model = casbin.Model()
    model.load_model(str(CASBIN_MODEL_PATH))
    enforcer = casbin.Enforcer(model)
    if not user.roles:
        return enforcer

    for role in user.roles:
        enforcer.add_grouping_policy(user.id, role.name)
        for permission in role.permissions:
            enforcer.add_policy(role.name, permission.resource, permission.action)
    return enforcer


def require_permission(resource: str, action: str) -> Callable:
    """Require a database-backed Casbin permission for the authenticated user."""

    def permission_dependency(
        token_payload: dict = Depends(get_current_user_jwt),
        db: Session = Depends(get_db),
    ) -> User:
        user_id = token_payload.get("sub")
        user = (
            db.query(User)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )
        if user is None or not user.roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        enforcer = _build_enforcer(user)
        if not enforcer.enforce(user.id, resource, action):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return permission_dependency
