import logging
from typing import Annotated

from database.database import Users, get_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.auth_models import write_user

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.auth_shemas import RefreshToken, TokenOut, User, UserIn, UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from utils.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_user_refresh,
    get_password_hash,
)

logger = logging.getLogger(__name__)

# Создаём API роутер.
router = APIRouter()


# async def user_login(current_user: Annotated[User, Depends(get_current_user)]):
@router.post("/auth/login", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def user_login(user_data: UserIn, session: AsyncSession = Depends(get_session)):
    """
    Регистрация пользователя в API

    Возвращает id пользователя username и telegram id.
    """

    logger.info(
        "user_login: registration attempt, username=%r, telegram_id=%s",
        user_data.username,
        user_data.telegram_id,
    )

    user_data.password = get_password_hash(user_data.password)
    user = await write_user(session=session, user_data=user_data)
    if user:
        logger.info(
            "user_login: registration success, user_id=%s, username=%r, telegram_id=%s",
            user.id,
            user.username,
            user.telegram_id,
        )
        return UserOut(
            id=user.id,
            username=user.username,
            telegram_id=user.telegram_id,
        )

    logger.warning(
        "user_login: registration conflict, username=%r, telegram_id=%s "
        "(user already exists)",
        user_data.username,
        user_data.telegram_id,
    )

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user already exists",
    )


@router.post("/auth/token", response_model=TokenOut, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    """
    Получение access и refresh токенов по логину и паролю

    Возвращает access toke, refresh token и тип токенов
    """

    logger.info(
        "login_for_access_token: login attempt, username=%r",
        form_data.username,
    )

    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        logger.warning(
            "login_for_access_token: login failed, username=%r (invalid credentials)",
            form_data.username,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token: str = create_access_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "access"},
    )
    refresh_token: str = create_refresh_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "refresh"},
    )

    logger.info(
        "login_for_access_token: login success, user_id=%s, username=%r, telegram_id=%s",
        user.id,
        user.username,
        user.telegram_id,
    )

    return TokenOut(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


# async def refresh_token(user: Annotated[User, Depends(get_current_user_refresh)]) -> Token:
@router.post(
    "/auth/refresh_token", response_model=TokenOut, status_code=status.HTTP_200_OK
)
async def access_refresh_token(
    refresh_token_data: RefreshToken, session: AsyncSession = Depends(get_session)
):
    """
    Обновить access и refresh токенов по refresh token

    Возвращает access toke, refresh token и тип токенов
    """

    logger.info(
        "access_refresh_token: refresh attempt",
    )

    try:
        user: Users = await get_current_user_refresh(
            session=session, refresh_token=refresh_token_data.refresh_token
        )
    except HTTPException as exc:
        # если get_current_user_refresh сам кидает HTTPException
        logger.warning(
            "access_refresh_token: refresh failed (invalid/expired token), "
            "status=%s, detail=%r",
            exc.status_code,
            exc.detail,
        )
        raise

    logger.info(
        "access_refresh_token: refresh success, user_id=%s, username=%r, telegram_id=%s",
        user.id,
        user.username,
        user.telegram_id,
    )

    access_token: str = create_access_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "access"},
    )
    refresh_token: str = create_refresh_token(
        data={"sub": user.username, "telegram_id": user.telegram_id, "type": "refresh"},
    )

    return TokenOut(
        access_token=access_token, refresh_token=refresh_token, token_type="Bearer"
    )


@router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    # Возвращает текущего пользователя

    logger.debug(
        "read_users_me: returning current user, username=%r, telegram_id=%s",
        current_user.username,
        current_user.telegram_id,
    )

    return current_user


@router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # Возвращает информацию о текущем пользователе

    logger.debug(
        "read_own_items: called for username=%r, telegram_id=%s",
        current_user.username,
        current_user.telegram_id,
    )

    return [{"item_id": "Foo", "owner": current_user.username}]
