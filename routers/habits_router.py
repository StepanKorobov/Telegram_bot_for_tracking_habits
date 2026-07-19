import logging
from typing import Annotated

from database.database import Habits, get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models.habits_models import (
    delete_habit_all,
    delete_habit_from_id,
    get_all_habit,
    get_habit_by_id,
    update_habit,
    write_habits,
)
from shemas.auth_shemas import User
from shemas.habits_shemas import (
    Habit,
    HabitsCreateOut,
    HabitsListOut,
    HabitsOut,
    HabitUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth_router import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/habits", response_model=HabitsListOut, status_code=status.HTTP_200_OK)
async def get_all_habits(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список всех привычек текущего активного пользователя.

    Возвращает отформатированный список привычек в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "get_all_habits: request, user_id=%s, username=%r",
        current_user.id,
        current_user.username,
    )

    habits_list = await get_all_habit(session=session, user_id=current_user.id)

    logger.info(
        "get_all_habits: response, user_id=%s, habits_count=%s",
        current_user.id,
        len(habits_list),
    )

    return HabitsListOut(habits=habits_list)


@router.post(
    "/habits", response_model=HabitsCreateOut, status_code=status.HTTP_201_CREATED
)
async def add_habits(
    habits: Habit,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Добавить новую привычку для текущего пользователя.

    Принимает данные привычки и сохраняет её в БД.
    Возвращает ID созданной привычки.
    """

    logger.info(
        "add_habits: create request, user_id=%s, name=%r",
        current_user.id,
        habits.habit_name,
    )

    habit_id = await write_habits(
        session=session, user_id=current_user.id, habit_data=habits
    )

    logger.info(
        "add_habits: created, user_id=%s, habit_id=%s, name=%r",
        current_user.id,
        habit_id,
        habits.habit_name,
    )

    return HabitsCreateOut(habit_id=habit_id)


@router.get(
    "/habits/{habit_id}", response_model=HabitsOut, status_code=status.HTTP_200_OK
)
async def get_habits_by_id(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Получить привычку текущего активного пользователя по ID привычки

    Возвращает отформатированную привычку в виде объекта HabitsOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "get_habits_by_id: request, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    habit = await get_habit_by_id(
        session=session, user_id=current_user.id, habit_id=habit_id
    )

    logger.info(
        "get_habits_by_id: found, user_id=%s, habit_id=%s, name=%r",
        current_user.id,
        habit_id,
        habit.habit_name,
    )

    return HabitsOut.model_validate(habit)


@router.put("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_habits(
    habit_id: int,
    habit: Habit,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить всю привычку текущего активного пользователя по ID привычки

    Принимает данные привычки и обновляет её в БД.
    """

    logger.info(
        "update_habits: full update request, user_id=%s, habit_id=%s, name=%r",
        current_user.id,
        habit_id,
        habit.habit_name,
    )

    await update_habit(
        session=session, user_id=current_user.id, habit_data=habit, habit_id=habit_id
    )

    logger.info(
        "update_habits: full update success, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    return None


@router.patch("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def partial_update_habits(
    habit_id: int,
    habit: HabitUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить частично привычку текущего активного пользователя по ID привычки

    Принимает данные привычки и обновляет её в БД.
    """

    logger.info(
        "partial_update_habits: partial update request, user_id=%s, habit_id=%s, "
        "fields=%s",
        current_user.id,
        habit_id,
        [name for name, value in habit.__dict__.items() if value is not None],
    )

    await update_habit(
        session=session, user_id=current_user.id, habit_data=habit, habit_id=habit_id
    )

    logger.info(
        "partial_update_habits: partial update success, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    return None


@router.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Удалить привычку текущего активного пользователя по ID привычки

    Принимает ID привычки и удаляет её в БД.
    """

    logger.info(
        "delete_habit: delete request, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    await delete_habit_from_id(
        session=session, user_id=current_user.id, habit_id=habit_id
    )

    logger.info(
        "delete_habit: delete success, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    return None


@router.delete("/habits", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habits_all(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Удалить все привычки текущего активного пользователя
    """

    logger.info(
        "delete_habits_all: delete all request, user_id=%s",
        current_user.id,
    )

    await delete_habit_all(user_id=current_user.id, session=session)

    logger.info(
        "delete_habits_all: delete all success, user_id=%s",
        current_user.id,
    )

    return None
