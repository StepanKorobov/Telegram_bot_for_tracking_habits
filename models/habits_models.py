import logging

from database.database import Habits, Users, get_session
from fastapi import Depends, HTTPException, status
from shemas.auth_shemas import User
from shemas.habits_shemas import Habit, HabitUpdate
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import user

from models.habit_tracking_models import write_track_habits

logger = logging.getLogger(__name__)


async def get_all_habit(session: AsyncSession, user_id: int) -> list[Habits]:
    """
    Получить все привычки пользователя из базы данных.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователь.

    Returns:
        Список словарей, где каждый словарь - представление одной привычки
        (результат вызова to_json() для объекта Habits).
    """

    logger.debug(
        "get_all_habit: querying habits for user_id=%s",
        user_id,
    )

    query = select(Habits).where(Habits.user_id == user_id)
    result = await session.execute(query)
    habits: list[Habits] = result.scalars().all()

    habits_list = [habit.to_json() for habit in habits]

    logger.info(
        "get_all_habit: found %s habits for user_id=%s",
        len(habits_list),
        user_id,
    )

    return habits_list


async def write_habits(session: AsyncSession, user_id: int, habit_data: Habit) -> int:
    """
    Создаёт привычку пользователя в БД и возвращает её ID.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователь.
        habit_data: Данные привычки (название и описание).

    Returns:
        ID созданной привычки.
    """

    logger.info(
        "write_habits: creating habit for user_id=%s, name=%r",
        user_id,
        habit_data.habit_name,
    )

    habits = Habits(**habit_data.__dict__, user_id=user_id)
    session.add(habits)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        logger.error(
            "write_habits: IntegrityError while creating habit, user_id=%s, "
            "name=%r, error=%r",
            user_id,
            habit_data.habit_name,
            exc,
        )
        raise

    logger.info(
        "write_habits: habit created, user_id=%s, habit_id=%s, name=%r",
        user_id,
        habits.id,
        habits.habit_name,
    )

    await write_track_habits(session=session, habit_id=habits.id)

    return habits.id


async def get_habit_by_id(session: AsyncSession, user_id: int, habit_id: int) -> Habits:
    """
    Получить привычку пользователя по ID привычки.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователь.
        habit_id: ID привычки

    Returns:
        Привычка (результат вызова to_json() для объекта Habits).
    """

    logger.debug(
        "get_habit_by_id: querying habit, user_id=%s, habit_id=%s",
        user_id,
        habit_id,
    )

    query = select(Habits).where(Habits.id == habit_id, Habits.user_id == user_id)
    result = await session.execute(query)
    habit = result.scalars().one_or_none()

    if habit is None:
        logger.warning(
            "get_habit_by_id: habit not found or not belongs to user, "
            "user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logger.info(
        "get_habit_by_id: habit found, user_id=%s, habit_id=%s, name=%r",
        user_id,
        habit_id,
        habit.habit_name,
    )

    return habit


async def update_habit(
    session: AsyncSession, user_id: int, habit_data: Habit | HabitUpdate, habit_id: int
) -> None:
    """
    Обновление привычки (как частичного, так и полного) у пользователя по ID привычки

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователь.
        habit_data: Данные привычки (название и описание). Могут содержать не полные данные (частичное обновление).
        habit_id: ID привычки

    Returns:
        None
    """

    habit: dict = {}

    if habit_data.habit_name:
        habit["habit_name"] = habit_data.habit_name
    if habit_data.description:
        habit["description"] = habit_data.description
    if habit_data.goal:
        habit["goal"] = habit_data.goal
    if habit_data.terms_date:
        habit["terms_date"] = habit_data.terms_date

    logger.info(
        "update_habit: updating habit, user_id=%s, habit_id=%s, fields=%s",
        user_id,
        habit_id,
        list(habit.keys()),
    )

    query = (
        update(Habits)
        .where(Habits.id == habit_id, Habits.user_id == user_id)
        .values(**habit)
    )

    try:
        await session.execute(query)
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        logger.error(
            "update_habit: IntegrityError, user_id=%s, habit_id=%s, error=%r",
            user_id,
            habit_id,
            exc,
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logger.debug(
        "update_habit: update executed for user_id=%s, habit_id=%s",
        user_id,
        habit_id,
    )


async def delete_habit_from_id(
    session: AsyncSession, user_id: int, habit_id: int
) -> None:
    """
    Удаление привычки пользователя по ID привычки

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.
        habit_id: ID привычки

    Returns:
        None

    Raises:
        HTTPException: 404, если привычка не найдена или не принадлежит пользователю.
    """

    logger.info(
        "delete_habit_from_id: deleting habit, user_id=%s, habit_id=%s",
        user_id,
        habit_id,
    )

    query = select(Habits).filter(Habits.id == habit_id, Habits.user_id == user_id)
    result = await session.execute(query)
    habit = result.scalars().one_or_none()

    if habit is None:
        logger.warning(
            "delete_habit_from_id: habit not found or not belongs to user, "
            "user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The habit was not found or does not belong to the current user.",
        )

    await session.delete(habit)
    await session.commit()

    logger.info(
        "delete_habit_from_id: habit deleted, user_id=%s, habit_id=%s",
        user_id,
        habit_id,
    )


async def delete_habit_all(session: AsyncSession, user_id: int) -> None:
    """
    Удалить все привычки пользователя по его ID.

    Args:
        session: Асинхронная сессия БД.
        user_id: ID текущего пользователя.

    Returns:
        None

    Raises:
        HTTPException: 404, если привычка не найдена или не принадлежит пользователю.
    """

    logger.info(
        "delete_habit_all: deleting all habits for user_id=%s",
        user_id,
    )

    query = delete(Habits).where(Habits.user_id == user_id)
    result = await session.execute(query)
    await session.commit()

    logger.info(
        "delete_habit_all: delete executed for user_id=%s, delete_count=%s",
        user_id,
        result.rowcount,
    )

    if result.rowcount == 0:
        logger.warning(
            "delete_habit_all: no habits to delete for user_id=%s",
            user_id,
        )
    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
