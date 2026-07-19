import logging
from typing import Annotated, Sequence

from database.database import Habits, get_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.habit_tracking_models import (
    get_habit_track_statistic_all,
    get_habit_track_statistic_from_habit_id,
    get_habit_tracking_from_user,
    habits_track_check,
    update_habit_track_alert_time,
)
from shemas.auth_shemas import User
from shemas.habit_tracking_shemas import (
    HabitIdCheck,
    HabitStatisticListOut,
    HabitsTrackingLitOut,
    HabitTrackAlertTime,
    StatusResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from routers.auth_router import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/habits_tracing",
    response_model=HabitsTrackingLitOut,
    status_code=status.HTTP_200_OK,
)
async def habits_tracing(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Получить список всех привычек текущего активного пользователя с отслеживанием.

    Возвращает отформатированный список привычек в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "habits_tracing: request, user_id=%s, username=%r",
        current_user.id,
        current_user.username,
    )

    result: Sequence[Habits] = await get_habit_tracking_from_user(
        session=session, user_id=current_user.id
    )

    logger.info(
        "habits_tracing: response, user_id=%s, habits_count=%s",
        current_user.id,
        len(result),
    )

    if result:
        return HabitsTrackingLitOut(habits=result)

    # Явно залогировать случай, когда нет привычек
    logger.debug(
        "habits_tracing: no habits for user_id=%s",
        current_user.id,
    )
    return HabitsTrackingLitOut(habits=[])


@router.post(
    "/habits_tracing/check",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
)
async def habits_tracing_check(
    current_user: Annotated[User, Depends(get_current_active_user)],
    habit_id: HabitIdCheck,
    session: AsyncSession = Depends(get_session),
):
    """
    Отметить выполнение привычки пользователя по ID привычки.

    Возвращает отформатированный список привычек в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "habits_tracing_check: request, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id.habit_id,
    )

    try:
        result: bool = await habits_track_check(
            session=session, user_id=current_user.id, habit_id=habit_id.habit_id
        )
    except HTTPException as exc:
        logger.warning(
            "habits_tracing_check: failed, user_id=%s, habit_id=%s, status=%s, detail=%r",
            current_user.id,
            habit_id.habit_id,
            exc.status_code,
            exc.detail,
        )
        raise

    if result:
        logger.info(
            "habits_tracing_check: success, user_id=%s, habit_id=%s",
            current_user.id,
            habit_id.habit_id,
        )
        return StatusResponse(result="ok")
    else:
        logger.error(
            "habits_tracing_check: unexpected result=False, user_id=%s, habit_id=%s",
            current_user.id,
            habit_id.habit_id,
        )
        raise HTTPException(
            status_code=404,
            detail="The habit was not found or does not belong to the current user",
        )


@router.post("/habits_tracking")
async def create_habits_tracking():
    # Создать трекинг для привычки НЕАКТИВЕН

    logger.warning("create_habits_tracking: endpoint not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented")


@router.patch(
    "/habits_tracking/alert_time",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
)
async def update_habits_tracking_alert_time(
    current_user: Annotated[User, Depends(get_current_active_user)],
    alert_time: HabitTrackAlertTime,
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить/Установить время оповещения о необходимости выполнить привычку.

    Возвращает отформатированный список привычек в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "update_habits_tracking_alert_time: request, user_id=%s, habit_id=%s, "
        "alert_time=%s",
        current_user.id,
        alert_time.habit_id,
        alert_time.alert_time,
    )

    try:
        await update_habit_track_alert_time(
            session=session,
            user_id=current_user.id,
            habit_id=alert_time.habit_id,
            alert_time=alert_time.alert_time,
        )
    except HTTPException as exc:
        logger.warning(
            "update_habits_tracking_alert_time: failed, user_id=%s, habit_id=%s, "
            "status=%s, detail=%r",
            current_user.id,
            alert_time.habit_id,
            exc.status_code,
            exc.detail,
        )
        raise

    logger.info(
        "update_habits_tracking_alert_time: success, user_id=%s, habit_id=%s",
        current_user.id,
        alert_time.habit_id,
    )

    return StatusResponse(result="ok")


@router.patch("/habits_tracking/count")
async def update_habits_tracking_count():
    # обновить количество НЕАКТИВЕН

    logger.warning("update_habits_tracking_count: endpoint not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/habits_tracking")
async def delete_habits_tracking():
    # Удалить трекинг НЕАКТИВЕН

    logger.warning("delete_habits_tracking: endpoint not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented")


# count +1


@router.get(
    "/habits_tracking/statistic",
    response_model=HabitStatisticListOut,
    status_code=status.HTTP_200_OK,
)
async def habits_tracking_statistic_all(
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Получить всю статистику по выполнению всех привычек.

    Возвращает отформатированный список привычек в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "habits_tracking_statistic_all: request, user_id=%s, username=%r",
        current_user.id,
        current_user.username,
    )

    result: Sequence[Habits] = await get_habit_track_statistic_all(
        session=session, user_id=current_user.id
    )

    logger.info(
        "habits_tracking_statistic_all: response, user_id=%s, habits_count=%s",
        current_user.id,
        len(result),
    )

    return HabitStatisticListOut(habits=result)


@router.get(
    "/habits_tracking/statistic/{habit_id}",
    response_model=HabitStatisticListOut,
    status_code=status.HTTP_200_OK,
)
async def habits_tracking_statistic(
    habit_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: AsyncSession = Depends(get_session),
):
    """
    Получить всю статистику выполнения привычки по ID.

    Возвращает отформатированный список из одной привычки в виде объекта HabitsListOut.
    Доступ разрешён только авторизованным и активным пользователям.
    """

    logger.info(
        "habits_tracking_statistic: request, user_id=%s, habit_id=%s",
        current_user.id,
        habit_id,
    )

    result: Habits = await get_habit_track_statistic_from_habit_id(
        session=session, user_id=current_user.id, habit_id=habit_id
    )

    if result is None:
        logger.warning(
            "habits_tracking_statistic: habit not found, user_id=%s, habit_id=%s",
            current_user.id,
            habit_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The habit was not found or does not belong to the current user",
        )

    logger.info(
        "habits_tracking_statistic: response, user_id=%s, habit_id=%s, "
        "stats_count=%s",
        current_user.id,
        habit_id,
        len(result.habit_tracking_statistics),
    )

    return HabitStatisticListOut(habits=[result])
