from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.authorization import (
    ManagedUserResponse,
    PermissionCreateRequest,
    PermissionResponse,
    RoleAssignmentRequest,
    RoleCreateRequest,
    RolePermissionAssignmentRequest,
    RoleResponse,
)
from app.services.authorization import (
    assign_role_to_user,
    attach_permission_to_role,
    create_permission,
    create_role,
    list_permissions,
    list_roles,
)
from app.shared.authorization import require_permission
from app.shared.dependencies import get_db

router = APIRouter(prefix="/authorization")


@router.get("/roles", response_model=list[RoleResponse])
def get_roles(
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return list_roles(db)


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_role(
    payload: RoleCreateRequest,
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    
    return create_role(db, payload)


@router.get("/permissions", response_model=list[PermissionResponse])
def get_permissions(
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return list_permissions(db)


@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_permission(
    payload: PermissionCreateRequest,
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return create_permission(db, payload)


@router.put("/users/{user_id}/role", response_model=ManagedUserResponse)
def assign_user_role(
    user_id: str,
    payload: RoleAssignmentRequest,
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return assign_role_to_user(db, user_id, payload.role)


@router.post(
    "/roles/{role_id}/permissions",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
)
def assign_permission_to_role(
    role_id: str,
    payload: RolePermissionAssignmentRequest,
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return attach_permission_to_role(db, role_id, payload.permission_id)
