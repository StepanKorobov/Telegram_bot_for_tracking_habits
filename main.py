from database.database import engine, Base
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from database.database import create_tables
from routers import auth_router, habits_router

tags_metadata = [
    {
        "name": "auth",
        "description": "Набор методов для регистрации и получения токенов.",
    },
    {
        "name": "habits",
        "description": "Набор методов для работы с привычками.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Эвент для выполнения кода перед запуском приложения"""
    await create_tables()

    yield


# Создаём экземпляр класса приложения с настройками
app: FastAPI = FastAPI(
    title="Habits app",
    description="Api для хранения данных о привычках пользователей",
    version="0.1.5",
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

# Роут для работы с авторизацией и аутентификацией
app.include_router(
    auth_router.router,
    prefix="/api",
    tags=["auth"],
)

# Роут
app.include_router(
    habits_router.router,
    prefix="/api",
    tags=["habits"],
)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
