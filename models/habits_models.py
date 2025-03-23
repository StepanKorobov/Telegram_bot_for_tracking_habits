from typing import List

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.database import Users, Habits, get_session


async def get_all_habit(user: Users, session: AsyncSession) -> List[Habits] | list:
    """
    Корутина для получения всех привычек у пользователя из БД

    :param session: Асинхронная сессия
    :type session: AsyncSession
    :param user: Пользователь
    :type user: Users

    :return:
    """
    query = select(Habits).filter(Habits.user_id == user.id)
    result = await session.execute(query)
    habits: List[Habits] = result.scalars().all()

    habits_list = [{"id": i_habits.id, "habit_name": i_habits.habit_name, "description": i_habits.description} for
                   i_habits in habits]

    return habits_list


async def write_habits(user: Users, habits: Habits, session: AsyncSession) -> int:
    """
    Корутина для записи привычки пользователя в БД

    :param user: Текущий пользователь
    :type user: Users
    :param habits: Привычка (название и описание)
    :type habits: Habits
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: ID созданной привычки
    :rtype: int
    """

    habits = Habits(**habits.__dict__, user_id=user.id)
    session.add(habits)

    await session.commit()

    return habits.id


async def get_habit_by_id(habit_id: int, session: AsyncSession) -> Habits:
    """
    Корутина для получения привычки по ID

    :param habit_id: ID привычки
    :type habit_id: int
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return:
    """

    query = select(Habits).filter(Habits.id == habit_id)
    result = await session.execute(query)
    habit = result.scalars().one_or_none()

    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return habit
