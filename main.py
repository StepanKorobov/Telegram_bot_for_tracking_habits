from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers import auth, user
from database.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Эвент-менеджер для выполнения кода до и после запуска приложения (создаёт таблицы в БД перед запуском приложения)"""
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
