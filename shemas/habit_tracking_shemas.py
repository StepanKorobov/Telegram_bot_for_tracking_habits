from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from shemas.habits_shemas import HabitsOut


class HabitsTracking(BaseModel):
    id: int = Field(
        ..., title="Habit ID", gt=0, description="Уникальный ID отслеживания привычки"
    )
    alert_time: date | None = Field(
        ..., title="Время оповещения", description="Время оповещения пользователя"
    )
    count: int = Field(
        ...,
        title="Количество выполнений привычки",
        description="Количество раз, сколько была выполнена привычка",
    )
    last_completion_date: datetime | None = Field(
        ...,
        title="Время выполнения привычки",
        description="Время последнего выполнения привычки",
    )

    model_config = ConfigDict(from_attributes=True)


class HabitsTrackingOut(HabitsOut):
    habit_tracking: HabitsTracking = Field(
        default_factory=HabitsTracking,
        description="Поле содержащее информацию об отслеживании привычки",
    )

    model_config = ConfigDict(from_attributes=True)


class HabitsTrackingLitOut(BaseModel):
    habits: list[HabitsTrackingOut] = Field(
        default_factory=list, description="Список привычек. Может быть пустым."
    )


class StatusResponse(BaseModel):
    result: str = Field(
        ...,
        title="Результат выполнения запроса",
        description="Содержит в себе результат выполнения запроса",
    )


class HabitIdCheck(BaseModel):
    habit_id: int = Field(..., title="Habit ID", description="ID привычки")


class HabitTrackAlertTime(BaseModel):
    habit_id: int = Field(
        ..., title="Habit ID", gt=0, description="Уникальный ID отслеживания привычки"
    )
    alert_time: time = Field(
        ..., title="Время оповещения", description="Время оповещения пользователя"
    )


class HabitStatisticDateOut(BaseModel):
    id: int = Field(
        ...,
        title="Habit tracking statistic ID",
        gt=0,
        description="уникальный ID статистики",
    )
    completion_date: datetime = Field(
        ...,
        title="Время выполнения привычки",
        description="Дата и время когда пользователь поставил отметку о выполнении привычки",
    )

    model_config = ConfigDict(from_attributes=True)


class HabitStatisticOut(HabitsOut):
    habit_tracking_statistics: list[HabitStatisticDateOut] = Field(
        default_factory=list, description="Список статистики. Может быть пустым."
    )

    model_config = ConfigDict(from_attributes=True)


class HabitStatisticListOut(BaseModel):
    habits: list[HabitStatisticOut] = Field(
        default_factory=list, description="Список привычек. Может быть пустым."
    )
