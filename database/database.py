from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    Relationship,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta

DATABASE_URL: str = "postgresql+asyncpg://admin:admin@127.0.0.1:5432/telegram"
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session: sessionmaker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
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
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Определяем связь One-to-Many с таблицей Habits
    habits: Mapped[Optional["Habits"]] = relationship(
        back_populates="user", cascade="all"
    )

    def __repr__(self):
        return f"username: {self.username}, telegram_id: {self.telegram_id}, is_active: {self.is_active}"

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
    goal: Mapped[str] = mapped_column(String(50), nullable=False)
    terms_date: Mapped[date] = mapped_column(Date, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Определяем связь Many-to-One с таблицей Users
    user: Mapped[List["Users"]] = Relationship(back_populates="habits")
    # # Определяем связь One-to-Many с таблицей HabitTracking
    habit_tracking: Mapped[Optional["HabitTracking"]] = relationship(
        back_populates="habits", cascade="all"
    )

    def __repr__(self):
        return f"habit_name: {self.habit_name}, description: {self.description}, goal: {self.goal}, terms_date: {self.terms_date},user_id: {self.user_id}"

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class HabitTracking(Base):
    """Таблица для отслеживания привычек"""

    # Название таблицы
    __tablename__ = "habit_tracking"

    # Определяем поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_completion_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    habits_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), nullable=False)

    # Определяем связь Many-to-One с таблицей Habits
    habits: Mapped[List["Habits"]] = Relationship(back_populates="habit_tracking")

    def __repr__(self):
        return f"alert_time: {self.alert_time}, count: {self.count}, last_completion_date: {self.last_completion_date},habits_id: {self.habits_id}"

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
