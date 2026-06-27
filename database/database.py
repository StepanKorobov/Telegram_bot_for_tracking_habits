from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta

DATABASE_URL: str = "postgresql+asyncpg://admin:admin@127.0.0.1:5432/telegram"
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
async_session: sessionmaker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    """Возвращает асинхронную сессию БД."""
    async with async_session() as session:
        yield session


async def create_tables():
    """Создает все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Users(Base):
    """Пользователь Telegram-приложения."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    habits: Mapped[list["Habits"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    habit_tracking_statistics: Mapped[list["HabitTrackingStatistics"]] = (
        relationship(back_populates="user", cascade="all, delete-orphan")
    )

    def __repr__(self):
        return (
            f"username: {self.username},"
            f"telegram_id: {self.telegram_id}"
            f"is_active: {self.is_active}"
        )

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Habits(Base):
    """Таблица привычек"""

    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    habit_name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    goal: Mapped[str] = mapped_column(String(50), nullable=False)
    terms_date: Mapped[date] = mapped_column(Date, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["Users"] = relationship(back_populates="habits")

    habit_tracking: Mapped["HabitTracking"] = relationship(
        back_populates="habits", cascade="all, delete-orphan"
    )

    habit_tracking_statistics: Mapped[list["HabitTrackingStatistics"]] = relationship(
        back_populates="habits", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"habit_name: {self.habit_name},"
            f"description: {self.description},"
            f"goal: {self.goal},"
            f"terms_date: {self.terms_date},"
            f"user_id: {self.user_id}"
        )

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class HabitTracking(Base):
    """Таблица отслеживания выполнения привычек."""

    __tablename__ = "habit_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_completion_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    habits_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    habits: Mapped["Habits"] = relationship(back_populates="habit_tracking")

    def __repr__(self):
        return (
            f"alert_time: {self.alert_time},"
            f"count: {self.count},"
            f"last_completion_date: {self.last_completion_date},"
            f"habits_id: {self.habits_id}"
        )

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class HabitTrackingStatistics(Base):
    """Таблица статистики выполнения привычек."""

    __tablename__ = "habit_tracking_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    completion_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    habit_id: Mapped[int] = mapped_column(
        ForeignKey("habits.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped[list["Users"]] = relationship(
        back_populates="habit_tracking_statistics"
    )

    habits: Mapped[list["Habits"]] = relationship(
        back_populates="habit_tracking_statistics"
    )

    def __repr__(self):
        return (
            f"completion_date: {self.completion_date},"
            f"user_id: {self.user_id},"
            f"habit_id: {self.habit_id}"
        )

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
