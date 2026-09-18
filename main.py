from fastapi import FastAPI

from app.routes.auth import router as auth_router

app = FastAPI(
    title="FastAPI JWT Authentication",
    description="Scalable, reusable JWT authentication service with access & refresh tokens",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])


@app.get("/", summary="Healthcheck")
def root():
    return {"status": "ok", "service": "FastAPI JWT Auth"}
