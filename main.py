from database.database import engine, Base
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from database.database import create_tables
from routers import auth, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Эвент для выполнения кода перед запуском приложения"""
    await create_tables()

    yield


# Создаём экземпляр класса приложения с настройками
app: FastAPI = FastAPI(title="Habits app", lifespan=lifespan)

# Роут
app.include_router(
    user.router,
    prefix="/api",
    tags=["users"],
)

# Роут для работы с авторизацией и аутентификацией
app.include_router(
    auth.router,
    prefix="/api",
    tags=["auth"],
)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
