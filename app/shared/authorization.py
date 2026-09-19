from collections.abc import Callable

import casbin
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.models.role import Role
from app.models.user import User
from app.shared.dependencies import get_current_user_jwt, get_db


CASBIN_RBAC_MODEL = """
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
"""


def _build_enforcer(user: User) -> casbin.Enforcer:
    model = casbin.Model()
    model.load_model_from_text(CASBIN_RBAC_MODEL)
    enforcer = casbin.Enforcer(model)
    if user.role is None:
        return enforcer

    enforcer.add_grouping_policy(user.id, user.role.name)
    for permission in user.role.permissions:
        enforcer.add_policy(user.role.name, permission.resource, permission.action)
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
            .options(selectinload(User.role).selectinload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )
        if user is None or user.role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        enforcer = _build_enforcer(user)
        if not enforcer.enforce(user.id, resource, action):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return permission_dependency
