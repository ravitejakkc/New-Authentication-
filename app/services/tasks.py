from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreateRequest, TaskStatusUpdateRequest


def create_task(db: Session, payload: TaskCreateRequest, current_user: User) -> Task:
    if payload.project_id is not None and db.get(Project, payload.project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    task = Task(
        title=payload.title,
        description=payload.description,
        project_id=payload.project_id,
        assigned_user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_assigned_tasks(db: Session, current_user: User) -> list[Task]:
    return list(
        db.scalars(
            select(Task)
            .where(Task.assigned_user_id == current_user.id)
            .order_by(Task.created_at.desc())
        ).all()
    )


def update_assigned_task_status(
    db: Session,
    task_id: str,
    payload: TaskStatusUpdateRequest,
    current_user: User,
) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.assigned_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task is not assigned to user")

    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


def delete_task_by_id(db: Session, task_id: str) -> None:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
