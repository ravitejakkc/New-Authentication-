from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.permission import Permission
from app.models.role import Role, RoleName
from app.models.user import User


DEFAULT_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("task", "read_assigned"),
    ("task", "create"),
    ("task", "update_assigned"),
    ("task", "delete"),
    ("project", "read_all"),
    ("user", "manage"),
)

DEFAULT_ROLE_PERMISSIONS: dict[RoleName, tuple[tuple[str, str], ...]] = {
    RoleName.MEMBER: (
        ("task", "read_assigned"),
        ("task", "create"),
        ("task", "update_assigned"),
    ),
    RoleName.ADMIN: DEFAULT_PERMISSIONS,
}


def seed_authorization_defaults(db: Session) -> None:
    """Create the standard database roles and permissions when they do not exist."""
    roles = {
        role.name: role
        for role in db.scalars(
            select(Role).options(selectinload(Role.permissions))
        ).all()
    }
    for role_name in RoleName:
        if role_name.value not in roles:
            role = Role(name=role_name.value)
            db.add(role)
            roles[role_name.value] = role
    db.flush()

    permissions = {
        (permission.resource, permission.action): permission
        for permission in db.scalars(select(Permission)).all()
    }
    for resource, action in DEFAULT_PERMISSIONS:
        if (resource, action) not in permissions:
            permission = Permission(resource=resource, action=action)
            db.add(permission)
            permissions[(resource, action)] = permission
    db.flush()

    for role_name, permission_keys in DEFAULT_ROLE_PERMISSIONS.items():
        role = roles[role_name.value]
        assigned = {(item.resource, item.action) for item in role.permissions}
        for permission_key in permission_keys:
            if permission_key not in assigned:
                role.permissions.append(permissions[permission_key])


def get_role_or_none(db: Session, role_name: RoleName) -> Role | None:
    return db.scalar(
        select(Role)
        .where(Role.name == role_name.value)
        .options(selectinload(Role.permissions))
    )


def get_role_or_404(db: Session, role_name: RoleName) -> Role:
    role = get_role_or_none(db, role_name)
    if role is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


def assign_role_to_user(db: Session, user_id: str, role_name: RoleName) -> User:
    from fastapi import HTTPException, status

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.role = get_role_or_404(db, role_name)
    db.commit()
    db.refresh(user)
    return user


def attach_permission_to_role(db: Session, role_id: str, permission_id: str) -> Role:
    from fastapi import HTTPException, status

    role = db.scalar(
        select(Role)
        .where(Role.id == role_id)
        .options(selectinload(Role.permissions))
    )
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    permission = db.get(Permission, permission_id)
    if permission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    return role


def list_roles(db: Session) -> list[Role]:
    return list(
        db.scalars(select(Role).options(selectinload(Role.permissions)).order_by(Role.name)).all()
    )


def list_permissions(db: Session) -> list[Permission]:
    return list(
        db.scalars(
            select(Permission).order_by(Permission.resource, Permission.action)
        ).all()
    )
