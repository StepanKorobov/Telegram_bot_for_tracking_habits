"""Файл для взаимодействия с БД"""

from functools import wraps
from typing import Union

from bot.database.database import Base, User, get_session


def create_tables():
    """Функция создания БД"""

    with get_session() as session:
        Base.metadata.create_all(bind=session)


# def with_current_user(func):
#     @wraps(func)
#     def wrapper(message, *args, **kwargs):
#         db = SessionLocal()
#         try:
#             tg_id = message.from_user.id
#             current_user = get_or_create_user(db, tg_id)
#             # если нужно, можно ещё положить db, но обычно достаточно юзера
#             return func(message, current_user=current_user, db=db, *args, **kwargs)
#         finally:
#             db.close()
#     return wrapper


def with_current_user(func):
    def wrapper(message, *args, **kwargs):
        db = 5
        try:
            tg_id = message.from_user.id
            current_user = "enisey"
            return func(message, current_user=current_user, db=db, *args, **kwargs)
        finally:
            a = 5

    return wrapper


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


def add_user(username: str, telegram_id: int, api_token, api_token_refresh):
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
