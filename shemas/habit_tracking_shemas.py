from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field, model_validator


class HabitCheck(BaseModel):
    habit_id: int = Field(
        ...,
        title="Habit ID",
    )
