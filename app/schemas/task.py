from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    project_id: str | None = Field(default=None, min_length=36, max_length=36)


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["TODO", "IN_PROGRESS", "DONE"]


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    assigned_user_id: str
    project_id: str | None

    model_config = ConfigDict(from_attributes=True)
