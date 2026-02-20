"""Файл для взаимодействия с БД"""
from typing import Union, Dict

from bot.database.database import Base, User, get_session


def create_tables():
    """Функция создания БД"""

    with get_session() as session:
        Base.metadata.create_all(bind=session)


def get_user_by_telegram_id(telegram_id: int) -> Union[User, None]:
    """
    Функция поиска пользователя по telegram_id

    :param telegram_id: Телеграм ID пользователя
    :type telegram_id: int
    :return: User or None
    :rtype: Union[User, None]
    """

    with get_session() as session:
        user: Union[User, None] = (
            session.query(User).filter(User.telegram_id == telegram_id).one_or_none()
        )

        return user


def add_user(username: str, telegram_id: int, api_token, api_token_refresh) -> None:
    """
    Функция добавления нового пользователя

    :param username: Имя пользователя в телеграм
    :type username: str
    :param telegram_id: Телеграм ID пользователя
    :type telegram_id: int
    :param api_token: API ключ
    :type api_token: str
    :param api_token_refresh: API ключ для обновления основного
    :type api_token_refresh: str
    :return: None
    :rtype: None
    """

    with get_session() as session:
        user = User(
            username=username,
            telegram_id=telegram_id,
            api_token=api_token,
            api_token_refresh=api_token_refresh,
        )

        session.add(user)
        session.commit()


def update_user_tokens(telegram_id: int, token_data: Dict[str, str]) -> None:
    with get_session() as session:
        user: User = session.query(User).filter(User.telegram_id == telegram_id).one_or_none()
        user.api_token = token_data.get("access_token")
        user.api_token_refresh = token_data.get("refresh_token")
        session.commit()
