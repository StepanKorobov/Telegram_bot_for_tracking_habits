from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.auth_shemas import User, UserInDB, Token, UserIn, RefreshToken

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session, Users
from models.auth_models import write_user
from utils.security import create_access_token, create_refresh_token, authenticate_user, get_current_active_user, \
    get_password_hash, get_current_user_refresh

# Создаём API роутер.
router = APIRouter()


# async def user_login(current_user: Annotated[User, Depends(get_current_user)]):
@router.post("/auth/login")
async def user_login(
        user_data: UserIn,
        session: AsyncSession = Depends(get_session)
) -> User:
    """
    Endpoint for user registration
    """

    user_data.password = get_password_hash(user_data.password)
    user = await write_user(session=session, user_data=user_data)
    if user:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=user.to_json())

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user already exists",
    )


@router.post("/auth/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session)
) -> Token:
    """
    The endpoint accepts the login and password, returning access and refresh tokens.
    """

    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "access"},
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "refresh"},
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


# async def refresh_token(user: Annotated[User, Depends(get_current_user_refresh)]) -> Token:
@router.post("/auth/refresh_token")
async def access_refresh_token(
        refresh_token_data: RefreshToken,
        session: AsyncSession = Depends(get_session)
) -> Token:
    """
    Endpoint for updating access and refresh tokens using a refresh token
    """

    user: Users = await get_current_user_refresh(token=refresh_token_data.refresh_token, session=session)

    access_token = create_access_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "access"},
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "refresh"},
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


@router.get("/users/me/", response_model=UserInDB)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
