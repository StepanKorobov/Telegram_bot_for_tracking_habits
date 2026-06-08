from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from shemas.auth_shemas import User
from routers.auth_router import get_current_active_user

from models.habits_models import get_all_habit, write_habits, get_habit_by_id, update_habit, delete_habit, \
    delete_habit_all
from models.habit_tracking_models import habits_track_check
from shemas.habit_tracking_shemas import HabitCheck
from database.database import get_session, Habits

router = APIRouter()


@router.get("/habits_tracing/")
async def habits_tracing():
    # Получить все привычки со временем
    pass


@router.post("/habits_tracing/check/")
async def habits_tracing_check(
        current_user: Annotated[User, Depends(get_current_active_user)],
        habit_id: HabitCheck,
        session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    Эндпоинт для отметки о выполнении привычки

    :param habit_id: ID привычки
    :type habit_id: int
    :param current_user: Текущий пользователь
    :type current_user: Annotated[User, Depends(get_current_active_user)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: ID, название, описание привычки
    :rtype: JSONResponse
    """

    result: bool = await habits_track_check(session=session, habit_id=habit_id.habit_id)

    if result:
        return JSONResponse(status_code=200, content={"result": "ok"})

    raise HTTPException(status_code=404, detail="The habit has already been completed today")


@router.post("/habits_tracking/")
async def create_habits_tracking():
    # Создать трекинг для привычки
    pass


@router.patch("/habits_tracking/alert_time/")
async def update_habits_tracking_alert_time():
    # Обновить время оповещения
    pass


@router.patch("/habits_tracking/count/")
async def update_habits_tracking_count():
    # обновить количество
    pass


@router.delete("/habits_tracking/")
async def delete_habits_tracking():
    # Удалить трекинг
    pass

# count +1
