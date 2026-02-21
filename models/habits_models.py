from typing import List

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user

from database.database import Users, Habits, get_session
from shemas.auth_shemas import User
from shemas.habits_shemas import Habit


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

    # habits_list = [{"id": i_habits.id, "habit_name": i_habits.habit_name, "description": i_habits.description} for
    #                i_habits in habits]
    habits_list = [i_habits.to_json() for i_habits in habits]

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


async def update_habit(habit_id: int, habit: Habit, user_id: int, session: AsyncSession) -> None:
    """
    Корутина для обновления привычки (как частичного, так и полного)

    :param habit_id: ID привычки
    :type habit_id: int
    :param habit: Название и описание привычки
    :type habit: Habits
    :param user_id: ID пользователя
    :type user_id: int
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Ничего
    :rtype: None
    """

    habits = dict()

    if habit.habit_name:
        habits["habit_name"] = habit.habit_name
    if habit.description:
        habits["description"] = habit.description

    query = update(Habits).filter(Habits.id == habit_id, Habits.user_id == user_id).values(**habits)

    try:
        await session.execute(query)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


async def delete_habit(habit_id: int, user_id: int, session: AsyncSession) -> None:
    """
    Корутина для удаления привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param user_id: ID пользователя
    :type user_id: int
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Ничего
    :rtype: None
    """

    query = select(Habits).filter(Habits.id == habit_id, Habits.user_id == user_id)
    result = await session.execute(query)
    habit = result.scalars().one_or_none()

    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await session.delete(habit)
    await session.commit()
