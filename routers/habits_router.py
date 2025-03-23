from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from shemas.auth_shemas import User
from routers.auth_router import get_current_active_user

from models.habits_models import get_habits, write_habits
from shemas.habits_shemas import Habit
from database.database import get_session

router = APIRouter()


@router.get("/habits")
async def get_all_habits(
        current_user: Annotated[User, Depends(get_current_active_user)],
        session: AsyncSession = Depends(get_session)):
    habits_list = await get_habits(session=session, user=current_user)

    return JSONResponse(status_code=200, content={"habits:": habits_list})


@router.post("/habits")
async def add_habits(current_user: Annotated[User, Depends(get_current_active_user)],
                     habits: Habit,
                     session: AsyncSession = Depends(get_session)):
    result = await write_habits(session=session, user=current_user, habits=habits)
    return JSONResponse(current_user.to_json())


@router.get("/habits/{habit_id}")
async def get_habits(habit_id: int,
                     current_user: Annotated[User, Depends(get_current_active_user)],
                     session: AsyncSession = Depends(get_session)):
    pass


@router.put("/habits/{habit_id}")
async def update_habits(habit_id: int,
                        current_user: Annotated[User, Depends(get_current_active_user)], ):
    pass


@router.patch("/habits/{habit_id}")
async def partial_update_habits(habit_id: int,
                                current_user: Annotated[User, Depends(get_current_active_user)], ):
    pass


@router.delete("/habits/{habit_id}")
async def delete_habits(habit_id: int,
                        current_user: Annotated[User, Depends(get_current_active_user)], ):
    pass
