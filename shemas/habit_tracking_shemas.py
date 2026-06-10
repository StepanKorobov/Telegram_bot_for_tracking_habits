from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator


class HabitCheck(BaseModel):
    habit_id: int = Field(
        ...,
        title="Habit ID",
    )


class HabitsStatisticOut(BaseModel):
    id: int = Field(..., gt=0)
    completion_date: datetime


class HabitsTrackOut(BaseModel):
    id: int = Field(..., gt=0)
    habit_name: str
    description: str
    goal: str
    terms_date: date
    habits_check_date: List[HabitsStatisticOut] | None
