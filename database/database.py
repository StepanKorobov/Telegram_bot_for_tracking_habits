from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    Relationship,
    declarative_base,
    mapped_column,
    sessionmaker, relationship,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta
import datetime
from typing import List, Optional

DATABASE_URL: str = "postgresql+asyncpg://admin:admin@127.0.0.1:5432/telegram"
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session: sessionmaker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base: DeclarativeMeta = declarative_base()


# session = async_session()

async def get_session() -> AsyncSession:
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Определяем связь One-to-Many с таблицей Habits
    habits: Mapped[Optional["Habits"]] = relationship(back_populates="user", cascade="all")

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Habits(Base):
    """Таблица привычек"""

    # Название таблицы
    __tablename__ = "habits"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Определяем связь Many-to-One с таблицей Users
    user: Mapped[List["Users"]] = Relationship(back_populates="habits", cascade="all")
    # # Определяем связь One-to-Many с таблицей HabitTracking
    habit_tracking: Mapped[Optional["HabitTracking"]] = relationship(back_populates="habits",
                                                                     cascade="all")


class HabitTracking(Base):
    """Таблица для уведомлений"""

    # Название таблицы
    __tablename__ = "habit_tracking"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    habits_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), nullable=False)

    # Определяем связь Many-to-One с таблицей Habits
    habits: Mapped[List["Habits"]] = Relationship(back_populates="habit_tracking", cascade="all")
