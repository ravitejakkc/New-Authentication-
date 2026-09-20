from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.shared.dependencies import get_db
from app.routes.auth import router as auth_router
from app.routes.authorization import router as authorization_router
from app.routes.projects import router as projects_router
from app.routes.tasks import router as tasks_router

app = FastAPI(
    title="FastAPI JWT Authentication",
    description="Scalable, reusable JWT authentication service with access & refresh tokens",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(authorization_router, tags=["Authorization"])
app.include_router(tasks_router)
app.include_router(projects_router)


@app.get("/", summary="Healthcheck")
def root():
    return {"status": "ok", "service": "FastAPI JWT Auth"}


@app.get("/health", summary="Healthcheck with database")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
