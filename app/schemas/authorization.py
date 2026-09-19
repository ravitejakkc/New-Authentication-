from pydantic import BaseModel, ConfigDict, Field

from app.models.role import RoleName


class PermissionResponse(BaseModel):
    id: str
    resource: str
    action: str

    model_config = ConfigDict(from_attributes=True)


class RoleResponse(BaseModel):
    id: str
    name: RoleName
    permissions: list[PermissionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoleAssignmentRequest(BaseModel):
    role: RoleName


class RolePermissionAssignmentRequest(BaseModel):
    permission_id: str = Field(min_length=36, max_length=36)


class ManagedUserResponse(BaseModel):
    id: str
    email: str
    role: RoleResponse

    model_config = ConfigDict(from_attributes=True)
