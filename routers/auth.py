import sys
import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.util import await_only

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.shema import User, UserInDB, Token, TokenData, UserIn, UserOut
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session, Users
from database.models import check_user_exist, write_user, get_user

# Секретный ключ, для подписания токена jwt
SECRET_KEY = "29f9d7c10178d852330fa3b08119de20cabe644b8403c022c16ce750e1a51dc3"
# Алгоритм используемый для подписи jwt
ALGORITHM = "HS256"
# Время жизни токена в минутах
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Время жизни токена для обновления jwt
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Контекст для шифрования, мы будем шифровать пароли
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Создаём API роутер.
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция для сравнения введённого пароля и пароля в БД (оба хэшированы)

    :param plain_password: Пароль пользователя после хэширования
    :type plain_password: str
    :param hashed_password: Пароль из БД
    :type hashed_password: str
    :return: True | False
    :rtype: bool
    """

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Функция для хэширования пароля

    :param password: Пароль введённый пользователем
    :type password: str
    :return: Хэш пароль
    :rtype: str
    """

    return pwd_context.hash(password)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> bool | Users:
    """
    Корутина для аутентификации пользователя

    :param session: Асинхронная сессия
    :type session: AsyncSession
    :param username: Имя пользователя
    :type username: str
    :param password: Пароль пользователя
    :type password: str
    :return: False | Users
    :rtype: bool | Users
    """

    # Получаем пользователя
    user: Users = await get_user(session=session, username=username)

    # Eсли не найден, то возвращаем False
    if not user:
        return False
    # Eсли пользователь не прошёл верификацию, то возвращаем False
    if not verify_password(password, user.password):
        return False

    # Возвращаем пользователя
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Функция для создания access токена

    :param data: Данные о пользователе
    :type data: dict
    :param expires_delta: Время жизни токена
    :type expires_delta: timedelta | None
    :return: jwt токен
    :rtype: str
    """

    # Копируем данные
    to_encode: dict = data.copy()
    # Проверяем указанно ли время жизни токена, если нет, устанавливаем 15 минут
    if expires_delta:
        expire: datetime = datetime.now(timezone.utc) + expires_delta
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=15)
    # Добавляем время жизни токена к данным
    to_encode.update({"exp": expire})
    # Создаём jwt токен
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Возвращаем jwt токен
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_session)
):
    """
    Корутина для получения текущего пользователя

    :param token: jwt токен от пользователя
    :type token: Annotated[str, Depends(oauth2_scheme)]
    :param session: Асинхронная сессия
    :type session: AsyncSession
    :return: Данные о пользователе
    :rtype: Users
    """

    # Исключение, если не удалось проверить данные, jwt токен
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем jwt токен
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Извлекаем из токена имя пользователя
        username: str = payload.get("sub")
        # Если отсутствуем имя пользователя, выкидываем ошибку
        if username is None:
            raise credentials_exception
        # Получаем данные о пользователе, через валидацию
        token_data = TokenData(username=username)
    except InvalidTokenError:
        # Ошибка при валидации, некорректный токен
        raise credentials_exception
    # Получаем пользователя
    user: Users = await get_user(session=session, username=token_data.username)
    # если пользователь не найден, не корректный токен
    if user is None:
        raise credentials_exception

    # Возвращаем найденного пользователя
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Корутина для проверки активен ли пользователь

    :param current_user: Пользователь для проверки
    :type current_user: Annotated[User, Depends(get_current_user)]

    :return:
    """

    # Если пользователь не активен, выбрасываем ошибку
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Возвращаем пользователя
    return current_user


@router.post("/auth/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: AsyncSession = Depends(get_session)
) -> Token:
    """
    Эндпоинт принимает логин и пароль, возвращая token
    """
    # Аутентифицируем пользователя
    user = await authenticate_user(session, form_data.username, form_data.password)
    # Если аутентификация не успешна, выкидываем исключение
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Задаём время жизни jwt токена
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Создаём jwt токен
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Возвращаем jwt токен
    return Token(access_token=access_token, token_type="bearer")


# async def user_login(current_user: Annotated[User, Depends(get_current_user)]):
@router.post("/auth/login")
async def user_login(
        user_data: UserIn,
        session: AsyncSession = Depends(get_session)
) -> User:
    """
    Эндпоинт для регистрации пользователей
    """
    # Хэшируем пароль
    user_data.password = get_password_hash(user_data.password)
    # Добавляем пользователя в БД
    user = await write_user(session=session, user_data=user_data)
    # если пользователь создан, возвращаем информацию о нём
    if user:
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=user.to_json())

    # Если такой пользователь уже существует, выкидывает исключение
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="This user already exists",
    )


@router.post("/auth/refresh_token")
async def refresh_token(user: UserIn):
    pass


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
