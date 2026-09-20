from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.project import ProjectCreateRequest, ProjectResponse
from app.services.projects import create_project, list_projects
from app.shared.authorization import require_permission
from app.shared.dependencies import get_db

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_project(
    payload: ProjectCreateRequest,
    _: User = Depends(require_permission("user", "manage")),
    db: Session = Depends(get_db),
):
    return create_project(db, payload)


@router.get("", response_model=list[ProjectResponse])
def read_all_projects(
    _: User = Depends(require_permission("project", "read_all")),
    db: Session = Depends(get_db),
):
    return list_projects(db)
