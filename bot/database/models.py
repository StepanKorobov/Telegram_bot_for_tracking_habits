import logging

from bot.database.database import Base, User, get_session
from sqlalchemy import exists

logger = logging.getLogger(__name__)


def create_tables():
    """Функция создания БД"""

    logger.info("create_tables: starting metadata.create_all")
    with get_session() as session:
        Base.metadata.create_all(bind=session)
    logger.info("create_tables: finished metadata.create_all")


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """
    Получить пользователя по telegram_id.

    Args:
        telegram_id: Telegram ID пользователя.

    Returns:
        Модель User в случае успеха, None в случае отсутствия пользователя.
    """

    logger.debug(
        "get_user_by_telegram_id: query start, telegram_id=%s",
        telegram_id,
    )

    with get_session() as session:
        user: User | None = (
            session.query(User).where(User.telegram_id == telegram_id).one_or_none()
        )

    if user:
        logger.info(
            "get_user_by_telegram_id: user found, telegram_id=%s, username=%r",
            telegram_id,
            user.username,
        )
    else:
        logger.info(
            "get_user_by_telegram_id: user not found, telegram_id=%s",
            telegram_id,
        )

    return user


def check_user_by_telegram_id(telegram_id: int) -> bool:
    """
    Проверка существования записи о пользователе в БД по telegram ID

    Args:
        telegram_id: Telegram ID пользователя.

    Returns:
        True в случае если пользователь есть, False в случае отсутствия записи о пользователе.
    """

    logger.debug(
        "check_user_by_telegram_id: query start, telegram_id=%s",
        telegram_id,
    )

    with get_session() as session:
        user_exist: bool = session.query(
            exists().where(User.telegram_id == telegram_id)
        ).scalar()

    logger.info(
        "check_user_by_telegram_id: result, telegram_id=%s, exists=%s",
        telegram_id,
        user_exist,
    )

    return user_exist


def add_user(
    username: str, telegram_id: int, api_token: str, api_token_refresh: str
) -> None:
    """
    Добавление нового пользователя в БД.

    Args:
        username: Имя пользователя в telegram.
        telegram_id: Telegram ID пользователя.
        api_token: Токен для аутентификации в API.
        api_token_refresh: Токен для обновления access токена.

    Returns:
        None.
    """

    logger.info(
        "add_user: creating user, telegram_id=%s, username=%r",
        telegram_id,
        username,
    )

    with get_session() as session:
        user = User(
            username=username,
            telegram_id=telegram_id,
            api_token=api_token,
            api_token_refresh=api_token_refresh,
        )

        session.add(user)
        session.commit()

    logger.info(
        "add_user: user created, telegram_id=%s, username=%r",
        telegram_id,
        username,
    )
    logger.debug(
        "add_user: tokens set for telegram_id=%s (access/refresh present=%s/%s)",
        telegram_id,
        bool(api_token),
        bool(api_token_refresh),
    )


def update_user_tokens(telegram_id: int, token_data: dict[str, str]) -> None:
    """
    Обновление токенов в БД по telegram ID.

    Args:
        telegram_id: Telegram ID пользователя.
        token_data: Словарь содержащий access, refresh токены, а так же тип токенов.

    Returns:
        None.
    """

    logger.info(
        "update_user_tokens: updating tokens, telegram_id=%s",
        telegram_id,
    )

    with get_session() as session:
        user: User = (
            session.query(User).filter(User.telegram_id == telegram_id).one_or_none()
        )

        if not user:
            logger.error(
                "update_user_tokens: user not found, telegram_id=%s",
                telegram_id,
            )
            return

        user.api_token = token_data.get("access_token")
        user.api_token_refresh = token_data.get("refresh_token")
        session.commit()

    logger.info(
        "update_user_tokens: tokens updated, telegram_id=%s",
        telegram_id,
    )
    logger.debug(
        "update_user_tokens: tokens present for telegram_id=%s (access/refresh=%s/%s)",
        telegram_id,
        bool(token_data.get("access_token")),
        bool(token_data.get("refresh_token")),
    )
