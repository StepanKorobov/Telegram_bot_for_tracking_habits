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
