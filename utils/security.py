import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.auth_shemas import User, TokenData
from jwt.exceptions import InvalidTokenError, InvalidSignatureError
# from passlib.context import CryptContext
from pwdlib import PasswordHash

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_session, Users
from models.auth_models import write_user, get_user

# Секретный ключ, для подписания access токена jwt
ACCESS_SECRET_KEY = "29f9d7c10178d852330fa3b08119de20cabe644b8403c022c16ce750e1a51dc3"
# Секретный ключ, для подписания refresh токена jwt
REFRESH_SECRET_KEY = "324a838022996764ace50de8abe555c92ef7308499f18aa77d4a9a91c31ee7c2"
# Алгоритм используемый для подписи jwt
ALGORITHM = "HS256"
# Время жизни токена в минутах 30
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Время жизни токена для обновления jwt
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Контекст для шифрования, мы будем шифровать пароли
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = PasswordHash.recommended()

# Схема для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


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

    # return pwd_context.verify(plain_password, hashed_password)
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Функция для хэширования пароля

    :param password: Пароль введённый пользователем
    :type password: str
    :return: Хэш пароль
    :rtype: str
    """

    # return pwd_context.hash(password)
    return password_hash.hash(password)


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

    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


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
        payload: dict = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return InvalidSignatureError

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    except InvalidTokenError:
        raise credentials_exception

    user: Users = await get_user(session=session, username=token_data.username)

    if user is None:
        raise credentials_exception

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

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def create_access_token(data: dict) -> str:
    """
    Функция для создания access токена

    :param data: Данные о пользователе
    :type data: dict
    :return: jwt токен
    :rtype: str
    """

    to_encode: dict = data.copy()

    if ACCESS_TOKEN_EXPIRE_MINUTES:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# Логика refresh_token вынесена отдельно.
# 1) для независимых проверок 2) для "безболезненного" вырезания функционала по обновлению токена


async def get_current_user_refresh(
        token: str,
        session: AsyncSession
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return InvalidSignatureError

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    except InvalidTokenError:
        raise credentials_exception

    user: Users = await get_user(session=session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def create_refresh_token(data: dict) -> str:
    """
    Функция для создания refresh токена

    :param data: Данные о пользователе
    :type data: dict
    :return: jwt токен
    :rtype: str
    """

    to_encode: dict = data.copy()

    if REFRESH_TOKEN_EXPIRE_DAYS:
        expire: datetime = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
