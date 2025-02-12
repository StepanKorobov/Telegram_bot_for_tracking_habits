from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.database import Users, Habits


async def get_habits(session: AsyncSession, user: Users):
    query = select(Habits).filter(Habits.user_id == user.id)
    result = await session.execute(query)
    habits: List[Habits] = result.scalars().all()
    habits_list = [{"id": i_habits.id, "habit_name": i_habits.habit_name, "description": i_habits.description} for
                   i_habits in habits]
    return habits_list


async def write_habits(session: AsyncSession, user: Users, habits: Habits):
    habits = Habits(**habits.__dict__, user_id=user.id)
    session.add(habits)
    await session.commit()
