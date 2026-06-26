from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Habit(BaseModel):
    habit_name: str = Field(
        ...,
        title="Habit name",
        max_length=50,
        min_length=1,
        description="Название привычки (1–50 символов)",
    )
    description: str = Field(
        ...,
        title="Habit description",
        max_length=250,
        min_length=1,
        description="Описание привычки (1–250 символов)",
    )
    goal: str = Field(
        ...,
        title="Habit goal",
        max_length=50,
        min_length=1,
        description="Цель по привычке (1–50 символов)",
    )
    terms_date: date = Field(
        ...,
        title="Habit terms date",
        description="Дата срока выполнения привычки (YYYY-MM-DD)",
    )


class HabitsOut(Habit):
    id: int = Field(
        ..., title="Habits ID", gt=0, description="Уникальный идентификатор привычки"
    )
    model_config = ConfigDict(from_attributes=True)


class HabitsListOut(BaseModel):
    habits: list[HabitsOut] = Field(
        default_factory=list, description="Список привычек. Может быть пустым."
    )


class HabitsCreateOut(BaseModel):
    habit_id: int = Field(..., title="Habit ID", description="ID созданной привычки")


class HabitUpdate(BaseModel):
    habit_name: Optional[str] = Field(
        None,
        title="Habit name",
        max_length=50,
        min_length=1,
        description="Название привычки (1–50 символов)",
    )
    description: Optional[str] = Field(
        None,
        title="Habit description",
        max_length=250,
        min_length=1,
        description="Описание привычки (1–250 символов)",
    )
    goal: Optional[str] = Field(
        None,
        title="Habit goal",
        max_length=50,
        min_length=1,
        description="Цель по привычке (1–50 символов)",
    )
    terms_date: Optional[date] = Field(
        None,
        title="Habit terms date",
        description="Дата срока выполнения привычки (YYYY-MM-DD)",
    )

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_field(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not any(v is not None for v in values.values()):
            raise ValueError("At least one field must be filled in")
        return values
