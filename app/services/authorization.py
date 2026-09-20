from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.permission import Permission
from app.models.role import Role, RoleName
from app.schemas.authorization import PermissionCreateRequest, RoleCreateRequest
from app.models.user import User


DEFAULT_ROLES: tuple[str, ...] = (
    RoleName.ADMIN.value,
    RoleName.MEMBER.value,
)

DEFAULT_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("task", "read_assigned"),
    ("task", "create"),
    ("task", "update_assigned"),
    ("task", "delete"),
    ("project", "read_all"),
    ("user", "manage"),
)

DEFAULT_ROLE_PERMISSIONS: dict[str, tuple[tuple[str, str], ...]] = {
    RoleName.MEMBER.value: (
        ("task", "read_assigned"),
        ("task", "create"),
        ("task", "update_assigned"),
    ),
    RoleName.ADMIN.value: DEFAULT_PERMISSIONS,
}


def _normalize_role_name(role_name: str | RoleName) -> str:
    value = role_name.value if isinstance(role_name, RoleName) else role_name
    return value.strip().upper()


def seed_authorization_defaults(db: Session) -> None:
    """Create the standard database roles and permissions when they do not exist."""
    roles = {
        role.name: role
        for role in db.scalars(
            select(Role).options(selectinload(Role.permissions))
        ).all()
    }
    for role_name in DEFAULT_ROLES:
        if role_name not in roles:
            role = Role(name=role_name)
            db.add(role)
            roles[role_name] = role
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
        role = roles[role_name]
        assigned = {(item.resource, item.action) for item in role.permissions}
        for permission_key in permission_keys:
            if permission_key not in assigned:
                role.permissions.append(permissions[permission_key])


def get_role_or_none(db: Session, role_name: str | RoleName) -> Role | None:
    normalized_role_name = _normalize_role_name(role_name)
    return db.scalar(
        select(Role)
        .where(Role.name == normalized_role_name)
        .options(selectinload(Role.permissions))
    )


def get_role_or_404(db: Session, role_name: str | RoleName) -> Role:
    role = get_role_or_none(db, role_name)
    if role is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


def create_role(db: Session, payload: RoleCreateRequest) -> Role:
    from fastapi import HTTPException, status

    role_name = _normalize_role_name(payload.name)
    existing = db.scalar(select(Role).where(Role.name == role_name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists",
        )

    role = Role(name=role_name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def assign_role_to_user(db: Session, user_id: str, role_name: str | RoleName) -> User:
    from fastapi import HTTPException, status

    user = db.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    role = get_role_or_404(db, role_name)
    if role not in user.roles:
        user.roles.append(role)
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


def create_permission(db: Session, payload: PermissionCreateRequest) -> Permission:
    from fastapi import HTTPException, status

    resource = payload.resource.strip()
    action = payload.action.strip()
    existing = db.scalar(
        select(Permission).where(
            Permission.resource == resource,
            Permission.action == action,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists",
        )

    permission = Permission(resource=resource, action=action)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


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
