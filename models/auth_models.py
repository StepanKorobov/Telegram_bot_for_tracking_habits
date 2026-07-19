import logging

from database.database import Users
from shemas.auth_shemas import UserIn
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logger = logging.getLogger(__name__)


# async def check_user_exist(session: AsyncSession, telegram_id: int):
#     return True


async def get_user(session: AsyncSession, username: str) -> Users | None:
    """
    Получить пользователя из БД по username

    Args:
        session: Асинхронная сессия БД.
        username: Имя пользователя

    Returns:
        Объект Users, либо None в случае если пользователь не найден.
    """

    logger.debug(
        "get_user: querying user by username=%r",
        username,
    )

    query = select(Users).where(Users.username == username)
    result = await session.execute(query)
    user: Users = result.scalar_one_or_none()

    if user:
        logger.info(
            "get_user: user found, id=%s, username=%r, telegram_id=%s",
            user.id,
            user.username,
            user.telegram_id,
        )
    else:
        logger.info(
            "get_user: user not found, username=%r",
            username,
        )

    return user


async def write_user(session: AsyncSession, user_data: UserIn) -> Users | None:
    """
    Создать запись о новом пользователе в БД

    Args:
        session: Асинхронная сессия БД.
        user_data: Данные о пользователе (логин, id, пароль).

    Returns:
        Объект Users, либо None в случае неуспешной записи.
    """

    logger.info(
        "write_user: creating user, username=%r, telegram_id=%s",
        user_data.username,
        user_data.telegram_id,
    )

    user = Users(
        username=user_data.username,
        telegram_id=user_data.telegram_id,
        password=user_data.password,
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        await session.rollback()

        logger.warning(
            "write_user: integrity error on user creation, "
            "username=%r, telegram_id=%s, error=%r",
            user_data.username,
            user_data.telegram_id,
            exc,
        )

        return None

    await session.refresh(user)

    logger.info(
        "write_user: user created successfully, id=%s, username=%r, telegram_id=%s",
        user.id,
        user.username,
        user.telegram_id,
    )

    return user
