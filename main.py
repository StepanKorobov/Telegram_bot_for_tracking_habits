from fastapi import FastAPI

from routers import user

app = FastAPI(title="Habits app")

app.include_router(
    user.router,
    prefix="/api",
    tags=["users"],
)
