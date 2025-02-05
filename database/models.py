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

DATABASE_URL = "postgresql+asyncpg://admin:admin@database:5432/telegram"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base: DeclarativeMeta = declarative_base()
session = async_session()


def sessions():
    pass


class Users(Base):
    """Таблица пользователей"""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(50), nullable=False)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    password: Mapped[int] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_users():
    async with async_session() as session:
        async with session.begin():
            users_query = select(Users)
            users_result: ChunkedIteratorResult = await session.execute(
                users_query
            )
            users: Users = users_result.scalars().all()

            if len(users) == 0:
                user1 = Users(user="Test", telegram_id=113, password=3123123, is_active=True)
                user2 = Users(user="Test1", telegram_id=113, password=3123123, is_active=True)
                user3 = Users(user="Test2", telegram_id=113, password=3123123, is_active=True)
                user4 = Users(user="Test3", telegram_id=113, password=3123123, is_active=True)
                session.add_all([user1, user2, user3, user4])
                session.commit()
