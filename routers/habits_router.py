from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from shemas.auth_shemas import User
from routers.auth_router import get_current_active_user

from models.habits_models import get_all_habit, write_habits, get_habit_by_id, update_habit, delete_habit
from shemas.habits_shemas import Habit, HabitsListOut, HabitsCreateOut, HabitsOut, HabitUpdate
from database.database import get_session, Habits

router = APIRouter()


@router.get("/habits", response_model=HabitsListOut)
async def get_all_habits(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для получения списка всех привычек пользователя

    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Список привычек
    :rtype: JSONResponse
    """

    habits_list = await get_all_habit(session=session, user=current_user)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"habits": habits_list})


@router.post("/habits", response_model=HabitsCreateOut)
async def add_habits(current_user: Annotated[User, Depends(get_current_active_user)],
                     habits: Habit,
                     session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для добавления новой привычки

    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param habits: Название и описание привычки
    :type habits: Habits
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Результат и id привычки
    :rtype: JSONResponse
    """

    habit = await write_habits(session=session, user=current_user, habits=habits)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"result": True, "habit_id": habit})


@router.get("/habits/{habit_id}", response_model=HabitsOut)
async def get_habits_by_id(habit_id: int,
                           current_user: Annotated[User, Depends(get_current_active_user)],
                           session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для получения привычки по ID

    :param habit_id: ID привычки
    :type habit_id: int
    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: ID, название, описание привычки
    :rtype: JSONResponse
    """
    habit = await get_habit_by_id(habit_id=habit_id, session=session)

    if habit.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The habit does not belong to this user")

    habit = {
        "id": habit.id,
        "habit_name": habit.habit_name,
        "description": habit.description,
    }

    return JSONResponse(status_code=status.HTTP_200_OK, content=habit)


@router.put("/habits/{habit_id}", response_model=HabitsCreateOut)
async def update_habits(habit_id: int,
                        habit: Habit,
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для обновления привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param habit: Название и описание привычки
    :type habit: Habits
    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Результат и id привычки
    :rtype: JSONResponse
    """

    await update_habit(habit_id=habit_id, habit=habit, user_id=current_user.id, session=session)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": True, "habit_id": habit_id})


@router.patch("/habits/{habit_id}")
async def partial_update_habits(habit_id: int,
                                habit: HabitUpdate,
                                current_user: Annotated[User, Depends(get_current_active_user)],
                                session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для частичного обновления привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param habit: Название и описание привычки
    :type habit: Habits
    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Результат и id привычки
    :rtype: JSONResponse
    """

    await update_habit(habit_id=habit_id, habit=habit, user_id=current_user.id, session=session)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": True, "habit_id": habit_id})


@router.delete("/habits/{habit_id}")
async def delete_habits(habit_id: int,
                        current_user: Annotated[User, Depends(get_current_active_user)],
                        session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для даления привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Результат и id привычки
    :rtype: JSONResponse
    """

    await delete_habit(habit_id=habit_id, user_id=current_user.id, session=session)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": True})
