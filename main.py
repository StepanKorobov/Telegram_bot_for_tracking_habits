from fastapi import FastAPI

from routers import auth, user

app = FastAPI(title="Habits app")

app.include_router(
    user.router,
    prefix="/api",
    tags=["users"],
)
app.include_router(
    auth.router,
    prefix="/api",
    tags=["auth"],
)
