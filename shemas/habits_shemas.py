from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, model_validator


class Habit(BaseModel):
    habit_name: str = Field(
        ...,
        title="Habit name",
        max_length=50,
        min_length=1,
    )
    description: str = Field(
        ...,
        title="Habit description",
        max_length=250,
        min_length=1,
    )
    goal: str = Field(
        title="Habit goal",
        max_length=50,
        min_length=1,
    )
    terms_date: date


class HabitsOut(Habit):
    id: int = Field(..., gt=0)


class HabitsListOut(BaseModel):
    habits: List[HabitsOut] | None


class HabitsCreateOut(BaseModel):
    result: bool
    habit_id: int


class HabitUpdate(BaseModel):
    habit_name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    terms_date: Optional[date] = None

    @model_validator(mode="before")
    def check_value(cls, values):
        if not any(values):
            raise ValueError("At least one field must be filled in")
        return values
