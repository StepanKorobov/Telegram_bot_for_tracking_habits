from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from shemas.auth_shemas import User
from routers.auth_router import get_current_active_user

from models.habits_models import get_all_habit, write_habits, get_habit_by_id, update_habit, delete_habit, \
    delete_habit_all
from models.habit_tracking_models import habits_track_check, get_habit_track_statistic_all, \
    get_habit_track_statistic_from_habit_id
from shemas.habit_tracking_shemas import HabitCheck, HabitsTrackOut
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

    result: bool = await habits_track_check(session=session, user_id=current_user.id, habit_id=habit_id.habit_id)

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

@router.get("/habits_tracking/statistic/", response_model=HabitsTrackOut)
async def habits_tracking_statistic_all(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: AsyncSession = Depends(get_session)):
    result = await get_habit_track_statistic_all(session=session, user_id=current_user.id)

    response = []
    for i_habit in result:
        res = {
            "id": i_habit.id,
            "habit_name": i_habit.habit_name,
            "description": i_habit.description,
            "goal": i_habit.goal,
            "terms_date": i_habit.terms_date,
            "habit_tracking_statistics": [{"id": i_statistic.id, "habits_check_date": i_statistic.completion_date} for
                                  i_statistic in i_habit.habit_tracking_statistics
                                  ]}
        response.append(res)

    return JSONResponse(status_code=200, content={"result": jsonable_encoder(response)})


@router.get("/habits_tracking/statistic/{habit_id}", response_model=HabitsTrackOut)
async def habits_tracking_statistic(
        habit_id: int,
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: AsyncSession = Depends(get_session)):
    result = await get_habit_track_statistic_from_habit_id(session=session, user_id=current_user.id,habit_id=habit_id)

    response = {
        "id": result.id,
        "habit_name": result.habit_name,
        "description": result.description,
        "goal": result.goal,
        "terms_date": result.terms_date,
        "habit_tracking_statistics": [{"id": i_statistic.id, "habits_check_date": i_statistic.completion_date} for
                              i_statistic in result.habit_tracking_statistics
                              ]}
    return JSONResponse(status_code=200, content={"result": jsonable_encoder(response)})
