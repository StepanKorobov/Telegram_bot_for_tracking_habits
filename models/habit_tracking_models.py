import datetime
from typing import Sequence

from database.database import (
    Habits,
    HabitTracking,
    HabitTrackingStatistics,
    Users,
    get_session,
)
from fastapi import Depends, HTTPException, status
from shemas.auth_shemas import User
from shemas.habits_shemas import Habit
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.functions import user


async def get_habit_tracking_from_user(
    session: AsyncSession, user_id: int
) -> Sequence[Habits]:
    """
    Получить привычку пользователя по ID привычки.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователь.

    Returns:
        Список привычек (результат вызова to_json() для объекта Habits, так же в каждый объект вложен список из объектов HabitTracking).
    """

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id)
        .options(selectinload(Habits.habit_tracking))
    )

    result = await session.execute(query)
    habits = result.scalars().all()

    return habits


async def write_track_habits(session: AsyncSession, habit_id: int) -> None:
    """
    Добавить отслеживание привычки в привычку

    Создаёт объект HabitTracking и добавляет его в объект Habits

    Args:
        session: Асинхронная сессия БД.
        habit_id: ID привычки

    Returns:
        None
    """

    habit_track = HabitTracking(
        count=0,
        habits_id=habit_id,
    )
    session.add(habit_track)
    await session.commit()


async def write_track_habits_statistic(
    session: AsyncSession, user_id: int, habit_id: int, date_time: datetime
) -> None:
    """
    добавляет запись в таблицу статистики выполнений привычек

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.
        habit_id: ID привычки
        date_time: Время выполнения привычки

    Returns:
        None
    """

    habit_statistic = HabitTrackingStatistics(
        completion_date=date_time,
        user_id=user_id,
        habit_id=habit_id,
    )
    session.add(habit_statistic)
    await session.commit()


async def habits_track_check(
    session: AsyncSession, user_id: int, habit_id: int
) -> bool:
    """
    Отметка о выполнении привычки

    Записывается в таблицу статистики, так же проверяет была ли привычка выполнена сегодня

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.
        habit_id: ID привычки

    Returns:
        None

    Raises:
        HTTPException: 404, если привычка не найдена или не принадлежит пользователю.
        HTTPException: 409, если привычка уже выполнялась сегодня.
    """

    query = (
        select(HabitTracking)
        .join(HabitTracking.habits)
        .where(HabitTracking.habits_id == habit_id, Habits.user_id == user_id)
    )
    result = await session.execute(query)
    habit_tracking = result.scalars().one_or_none()

    if habit_tracking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    current_date_time = datetime.datetime.now()

    if habit_tracking.last_completion_date is None:
        habit_tracking.last_completion_date = current_date_time
        habit_tracking.count += 1
        await session.commit()
        await write_track_habits_statistic(
            session=session,
            user_id=user_id,
            habit_id=habit_id,
            date_time=current_date_time,
        )
        return True

    current_date = datetime.datetime.date(current_date_time)
    habit_tracking_date = datetime.datetime.date(habit_tracking.last_completion_date)

    if current_date > habit_tracking_date:
        habit_tracking.last_completion_date = current_date_time
        habit_tracking.count += 1
        await session.commit()
        await write_track_habits_statistic(
            session=session,
            user_id=user_id,
            habit_id=habit_id,
            date_time=current_date_time,
        )
        return True
    else:
        raise HTTPException(
            status_code=409, detail="The habit has already been completed today"
        )


async def get_habit_track_statistic_all(
    session: AsyncSession, user_id: int
) -> Sequence[Habits]:
    """
    Получить всю статистику пользователя по всем привычкам

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.

    Returns:
        None
    """

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id)
        .options(selectinload(Habits.habit_tracking_statistics))
    )

    result = await session.execute(query)
    habits = result.scalars().all()

    return habits


async def get_habit_track_statistic_from_habit_id(
    session: AsyncSession, user_id: int, habit_id: int
) -> Habits:
    """
    Получить всю статистику пользователя по конкретной привычке

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.
        habit_id: ID привычки

    Returns:
        None
    """

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id, Habits.id == habit_id)
        .options(selectinload(Habits.habit_tracking_statistics))
    )
    result = await session.execute(query)
    habits = result.scalars().one_or_none()

    return habits


async def update_habit_track_alert_time(
    session: AsyncSession, user_id: int, habit_id: int, alert_time: datetime.time
) -> None:
    """
    Устанавливает/Обновляет время оповещения о необходимости выполнить привычку.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.
        habit_id: ID привычки
        alert_time: Время оповещения

    Returns:
        None

    Raises:
        HTTPException: 404, если привычка не найдена или не принадлежит пользователю.
    """

    subquery = (
        select(Habits.id)
        .where(Habits.id == habit_id, Habits.user_id == user_id)
        .scalar_subquery()
    )

    query = (
        update(HabitTracking)
        .where(HabitTracking.habits_id == subquery)
        .values(alert_time=alert_time)
    )
    try:
        await session.execute(query)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The habit was not found or does not belong to the current user",
        )
