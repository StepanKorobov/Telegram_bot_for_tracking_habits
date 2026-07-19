import datetime
import logging
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

logger = logging.getLogger(__name__)


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

    logger.debug(
        "get_habit_tracking_from_user: querying habits for user_id=%s",
        user_id,
    )

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id)
        .options(selectinload(Habits.habit_tracking))
    )

    result = await session.execute(query)
    habits = result.scalars().all()

    logger.info(
        "get_habit_tracking_from_user: found %s habits for user_id=%s",
        len(habits),
        user_id,
    )

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

    logger.info(
        "write_track_habits: creating HabitTracking for habit_id=%s",
        habit_id,
    )

    habit_track = HabitTracking(
        count=0,
        habits_id=habit_id,
    )
    session.add(habit_track)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        logger.error(
            "write_track_habits: IntegrityError for habit_id=%s, error=%r",
            habit_id,
            exc,
        )
        raise
    else:
        logger.info(
            "write_track_habits: HabitTracking created for habit_id=%s",
            habit_id,
        )


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

    logger.debug(
        "write_track_habits_statistic: inserting stat, user_id=%s, habit_id=%s, "
        "completion_date=%s",
        user_id,
        habit_id,
        date_time,
    )

    habit_statistic = HabitTrackingStatistics(
        completion_date=date_time,
        user_id=user_id,
        habit_id=habit_id,
    )
    session.add(habit_statistic)

    try:
        await session.commit()
    except IntegrityError as exc:
        logger.error(
            "write_track_habits_statistic: IntegrityError, user_id=%s, habit_id=%s, "
            "error=%r",
            user_id,
            habit_id,
            exc,
        )
        raise
    else:
        logger.info(
            "write_track_habits_statistic: stat saved, user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )


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

    logger.info(
        "habits_track_check: checking habit completion, user_id=%s, habit_id=%s",
        user_id,
        habit_id,
    )

    query = (
        select(HabitTracking)
        .join(HabitTracking.habits)
        .where(HabitTracking.habits_id == habit_id, Habits.user_id == user_id)
    )
    result = await session.execute(query)
    habit_tracking = result.scalars().one_or_none()

    if habit_tracking is None:
        logger.warning(
            "habits_track_check: HabitTracking not found for user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    current_date_time = datetime.datetime.now()

    logger.debug(
        "habits_track_check: last_completion_date=%s, current_datetime=%s, count=%s",
        habit_tracking.last_completion_date,
        current_date_time,
        habit_tracking.count,
    )

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

        logger.info(
            "habits_track_check: first completion recorded, user_id=%s, habit_id=%s, "
            "count=%s",
            user_id,
            habit_id,
            habit_tracking.count,
        )

        return True

    current_date = datetime.datetime.date(current_date_time)
    habit_tracking_date = datetime.datetime.date(habit_tracking.last_completion_date)

    logger.debug(
        "habits_track_check: current_date=%s, last_date=%s",
        current_date,
        habit_tracking_date,
    )

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

        logger.info(
            "habits_track_check: completion recorded, user_id=%s, habit_id=%s, "
            "count=%s",
            user_id,
            habit_id,
            habit_tracking.count,
        )
        return True
    else:
        logger.warning(
            "habits_track_check: habit already completed today, user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
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

    logger.debug(
        "get_habit_track_statistic_all: querying stats for user_id=%s",
        user_id,
    )

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id)
        .options(selectinload(Habits.habit_tracking_statistics))
    )

    result = await session.execute(query)
    habits = result.scalars().all()

    logger.info(
        "get_habit_track_statistic_all: found %s habits with stats for user_id=%s",
        len(habits),
        user_id,
    )

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

    logger.debug(
        "get_habit_track_statistic_from_habit_id: querying stats, user_id=%s, "
        "habit_id=%s",
        user_id,
        habit_id,
    )

    query = (
        select(Habits)
        .join(Habits.user)
        .where(Users.id == user_id, Habits.id == habit_id)
        .options(selectinload(Habits.habit_tracking_statistics))
    )
    result = await session.execute(query)
    habit = result.scalars().one_or_none()

    if habit:
        logger.info(
            "get_habit_track_statistic_from_habit_id: habit found, user_id=%s, "
            "habit_id=%s, stats_count=%s",
            user_id,
            habit_id,
            len(habit.habit_tracking_statistics),
        )
    else:
        logger.warning(
            "get_habit_track_statistic_from_habit_id: habit not found, user_id=%s, "
            "habit_id=%s",
            user_id,
            habit_id,
        )

    return habit


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

    logger.info(
        "update_habit_track_alert_time: updating alert_time, user_id=%s, habit_id=%s, "
        "alert_time=%s",
        user_id,
        habit_id,
        alert_time,
    )

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
        logger.info(
            "update_habit_track_alert_time: alert_time updated, user_id=%s, "
            "habit_id=%s",
            user_id,
            habit_id,
        )
    except IntegrityError as exc:
        await session.rollback()
        logger.error(
            "update_habit_track_alert_time: IntegrityError, user_id=%s, "
            "habit_id=%s, error=%r",
            user_id,
            habit_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The habit was not found or does not belong to the current user",
        )
