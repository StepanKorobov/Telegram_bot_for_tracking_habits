import logging
from contextlib import contextmanager

from sqlalchemy import BigInteger, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)


# session = Session()


@contextmanager
def get_session():
    """Контекстный менеджер для получения сессии"""
    session = Session()
    logger.debug("DB session created: %r", session)

    try:
        yield session
        logger.debug("DB session scope completed successfully: %r", session)
    except Exception as exc:
        logger.exception("DB session error, rolling back: %r, exc=%r", session, exc)
        session.rollback()
    finally:
        session.close()
        logger.debug("DB session closed: %r", session)


class Base(DeclarativeBase):
    """Базовый класс таблиц"""

    pass


class User(Base):
    """Таблица пользователей с токенами"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    api_token: Mapped[str] = mapped_column(String(256))
    api_token_refresh: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        return (
            f"username: {self.username},"
            f"telegram_id: {self.telegram_id},"
            f"api_token: {self.api_token},"
            f"api_token_refresh: {self.api_token_refresh}"
        )

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
