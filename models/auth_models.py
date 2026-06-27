from database.database import Users
from shemas.auth_shemas import UserIn
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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

    query = select(Users).where(Users.username == username)
    result = await session.execute(query)
    user: Users = result.scalar_one_or_none()

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

    user = Users(
        username=user_data.username,
        telegram_id=user_data.telegram_id,
        password=user_data.password,
    )
    session.add(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()

        return None

    return user
