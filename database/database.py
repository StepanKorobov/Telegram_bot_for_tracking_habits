from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    Relationship,
    declarative_base,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.future import select
import datetime
from typing import List

DATABASE_URL: str = "postgresql+asyncpg://admin:admin@database:5432/telegram"
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session: sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base: DeclarativeMeta = declarative_base()


# session = async_session()


async def sessions() -> AsyncSession:
    """Корутина для создания асинхронной сессии"""
    async with async_session() as session:
        yield session


async def create_tables():
    """Корутина для создания таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Users(Base):
    """Таблица пользователей"""

    # Название таблицы
    __tablename__ = "users"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    password: Mapped[int] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class Habits(Base):
    """Таблица привычек"""

    # Название таблицы
    __tablename__ = "habits"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)

    # Определяем связь
    user_id: Mapped[List["Users"]] = Relationship(back_populates="habits", cascade="all, delete-orphan")


class HabitTracking(Base):
    """Таблица для уведомлений"""

    # Название таблицы
    __tablename__ = "habittracking"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Определяем связь
    habit_id: Mapped[List["Habits"]] = Relationship(backref="habit_tracking", cascade="all, delete-orphan")
