from bot.database.database import Base, User, get_session
from sqlalchemy import exists


def create_tables():
    """Функция создания БД"""

    with get_session() as session:
        Base.metadata.create_all(bind=session)


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """
    Получить пользователя по telegram_id.

    Args:
        telegram_id: Telegram ID пользователя.

    Returns:
        Модель User в случае успеха, None в случае отсутствия пользователя.
    """

    with get_session() as session:
        user: User | None = (
            session.query(User).where(User.telegram_id == telegram_id).one_or_none()
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

    with get_session() as session:
        user_exist: bool = session.query(
            exists().where(User.telegram_id == telegram_id)
        ).scalar()

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

    with get_session() as session:
        user = User(
            username=username,
            telegram_id=telegram_id,
            api_token=api_token,
            api_token_refresh=api_token_refresh,
        )

        session.add(user)
        session.commit()


def update_user_tokens(telegram_id: int, token_data: dict[str, str]) -> None:
    """
    Обновление токенов в БД по telegram ID.

    Args:
        telegram_id: Telegram ID пользователя.
        token_data: Словарь содержащий access, refresh токены, а так же тип токенов.

    Returns:
        None.
    """

    with get_session() as session:
        user: User = (
            session.query(User).filter(User.telegram_id == telegram_id).one_or_none()
        )
        user.api_token = token_data.get("access_token")
        user.api_token_refresh = token_data.get("refresh_token")
        session.commit()
