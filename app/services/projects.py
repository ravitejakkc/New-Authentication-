from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreateRequest


def create_project(db: Session, payload: ProjectCreateRequest) -> Project:
    name = payload.name.strip()
    existing = db.scalar(select(Project).where(Project.name == name))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already exists",
        )

    project = Project(name=name, description=payload.description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session) -> list[Project]:
    return list(db.scalars(select(Project).order_by(Project.name)).all())
