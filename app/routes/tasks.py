from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskResponse, TaskStatusUpdateRequest
from app.services.tasks import (
    create_task as create_task_service,
    delete_task_by_id,
    list_assigned_tasks,
    update_assigned_task_status,
)
from app.shared.authorization import require_permission
from app.shared.dependencies import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateRequest,
    current_user: User = Depends(require_permission("task", "create")),
    db: Session = Depends(get_db),
):
    return create_task_service(db, payload, current_user)


@router.get("/assigned", response_model=list[TaskResponse])
def read_assigned_tasks(
    current_user: User = Depends(require_permission("task", "read_assigned")),
    db: Session = Depends(get_db),
):
    return list_assigned_tasks(db, current_user)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: str,
    payload: TaskStatusUpdateRequest,
    current_user: User = Depends(require_permission("task", "update_assigned")),
    db: Session = Depends(get_db),
):
    return update_assigned_task_status(db, task_id, payload, current_user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    _: User = Depends(require_permission("task", "delete")),
    db: Session = Depends(get_db),
):
    delete_task_by_id(db, task_id)
