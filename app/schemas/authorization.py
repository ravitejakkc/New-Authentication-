from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    id: str
    resource: str
    action: str

    model_config = ConfigDict(from_attributes=True)


class PermissionCreateRequest(BaseModel):
    resource: str = Field(min_length=1, max_length=50)
    action: str = Field(min_length=1, max_length=50)


class RoleResponse(BaseModel):
    id: str
    name: str
    permissions: list[PermissionResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class RoleAssignmentRequest(BaseModel):
    role: str = Field(min_length=1, max_length=50)


class RolePermissionAssignmentRequest(BaseModel):
    permission_id: str = Field(min_length=36, max_length=36)


class ManagedUserResponse(BaseModel):
    id: str
    email: str
    roles: list[RoleResponse]

    model_config = ConfigDict(from_attributes=True)
