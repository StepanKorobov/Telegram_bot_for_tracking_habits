from typing import List

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.functions import user

from database.database import Users, Habits, HabitTracking, get_session
from shemas.auth_shemas import User
from shemas.habits_shemas import Habit


async def write_track_habits(session: AsyncSession, habit_id: int):
    habit_track = HabitTracking(
        count=0,
        habits_id=habit_id,
    )
    session.add(habit_track)
    await session.commit()
