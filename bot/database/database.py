"""Файл настройки сессии и создания БД"""

from contextlib import contextmanager

from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)


# session = Session()


@contextmanager
def get_session():
    """Контекстный менеджер для получения сессии"""
    session = Session()
    try:
        yield session
    except Exception:
        session.rollback()
    finally:
        session.close()


class Base(DeclarativeBase):
    """Базовый класс таблиц"""

    pass


class User(Base):
    """Таблица пользователей с токенами"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    api_token: Mapped[str] = mapped_column(String)
    api_token_refresh: Mapped[str] = mapped_column(String)
