from fastapi import APIRouter

router = APIRouter()


@router.get("/habits_tracing/")
async def habits_tracing():
    # Получить все привычки со временем
    pass


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
