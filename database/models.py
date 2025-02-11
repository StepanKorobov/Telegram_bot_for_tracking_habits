from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.database import Users


async def check_user_exist(session: AsyncSession, telegram_id: int):
    return True


async def write_user(session: AsyncSession, user_data):
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

        return False

    return user
