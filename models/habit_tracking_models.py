import datetime
from typing import List

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user
from sqlalchemy.orm import selectinload

from database.database import Users, Habits, HabitTracking, get_session, HabitTrackingStatistics
from shemas.auth_shemas import User
from shemas.habits_shemas import Habit


async def write_track_habits(session: AsyncSession, habit_id: int) -> None:
    """
    Добавить запись в отслеживание привычки
    """
    habit_track = HabitTracking(
        count=0,
        habits_id=habit_id,
    )
    session.add(habit_track)
    await session.commit()


async def write_track_habits_statistic(session: AsyncSession, user_id: int, habit_id: int, date_time) -> None:
    habit_statistic = HabitTrackingStatistics(
        completion_date=date_time,
        user_id=user_id,
        habit_id=habit_id,
    )
    session.add(habit_statistic)
    await session.commit()


async def habits_track_check(session: AsyncSession, user_id: int, habit_id: int) -> bool:
    """
    Корутина для отметки выполнения привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: bool
    :rtype: bool
    """

    query = select(HabitTracking).filter(HabitTracking.habits_id == habit_id)
    result = await session.execute(query)
    habit_tracking = result.scalars().one_or_none()

    if habit_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    current_date_time = datetime.datetime.now()

    if habit_tracking.last_completion_date is None:
        habit_tracking.last_completion_date = current_date_time
        habit_tracking.count += 1
        await session.commit()
        await write_track_habits_statistic(session=session, user_id=user_id, habit_id=habit_id,
                                           date_time=current_date_time)
        return True

    current_date = datetime.datetime.date(current_date_time)
    habit_tracking_date = datetime.datetime.date(habit_tracking.last_completion_date)

    if current_date > habit_tracking_date:
        habit_tracking.last_completion_date = current_date_time
        habit_tracking.count += 1
        await session.commit()
        await write_track_habits_statistic(session=session, user_id=user_id, habit_id=habit_id,
                                           date_time=current_date_time)
        return True

    return False


async def get_habit_track_statistic_all(session: AsyncSession, user_id: int):
    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id)
        .options(selectinload(Habits.habit_tracking_statistics))
    )
    result = await session.execute(query)
    habits = result.scalars().all()

    return habits


async def get_habit_track_statistic_from_habit_id(session: AsyncSession, user_id: int, habit_id: int) -> None:
    pass
