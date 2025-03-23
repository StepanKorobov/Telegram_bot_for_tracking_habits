from typing import List, Optional

from pydantic import BaseModel, Field


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
        max_length=150,
        min_length=1,
    )


class HabitsFromIDOut(BaseModel):
    id: int
    habit_name: str
    description: str


class HabitsOut(BaseModel):
    habits: List[HabitsFromIDOut] | None


class HabitsCreateOut(BaseModel):
    result: bool
    habit_id: int
