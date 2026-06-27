from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from database.database import Users, get_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidSignatureError, InvalidTokenError
from models.auth_models import get_user, write_user

# from passlib.context import CryptContext
from pwdlib import PasswordHash

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.auth_shemas import TokenData, User
from sqlalchemy.ext.asyncio import AsyncSession

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
    Cравнение введённого пароля и пароля в БД (оба хэшированы)

    Args:
        plain_password: Пароль пользователя после хэширования
        hashed_password: Пароль из БД

    Returns:
        True либо False, в зависимости одинаковый хеш или нет
    """

    # return pwd_context.verify(plain_password, hashed_password)
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля (как для проверки, так и для хранения в БД)

    Args:
        password: Пароль пользователя

    Returns:
        зашифрованный пароль
    """

    # return pwd_context.hash(password)
    return password_hash.hash(password)


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> bool | Users:
    """
    Аутентификация пользователя по логину и паролю

    Args:
        session: Асинхронная сессия БД.
        username: Имя пользователя
        password: Пароль пользователя

    Returns:
        Модель пользователя Users, либо False в случе если пользователь не найден или пароль не верный
    """

    user: Users = await get_user(session=session, username=username)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> Users:
    """
    Получение текущего пользователя из БД

    Извлекает информацию о пользователе по токену из БД

    Args:
        token: Access токен пользователя
        session: Асинхронная сессия БД.

    Returns:
        None

    Raises:
        HTTPException: 401, если токен невалидный, либо некорректный тип токена
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

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
    Получение текущего активного пользователя из БД

    Проверяет активен ли пользователь

    Args:
        current_user: Текущий пользователь полученный из БД через зависимости

    Returns:
        Модель пользователя User
    """

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
    Генерация access токена

    Args:
        data: Словарь содержащий данные о пользователе и типе токена

    Returns:
        Access токен
    """

    to_encode: dict = data.copy()

    if ACCESS_TOKEN_EXPIRE_MINUTES:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# Логика refresh_token вынесена отдельно.
# 1) для независимых проверок 2) для "безболезненного" вырезания функционала по обновлению токена


async def get_current_user_refresh(session: AsyncSession, refresh_token: str):
    """
    Получение пользователя из БД по refresh токену

    Извлекает запись из БД

    Args:
        session: Асинхронная сессия БД.
        refresh_token: refresh token

    Returns:
        None

    Raises:
        HTTPException: 401, если тип токена не верный.
        InvalidTokenError: в случае невалидного токена.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict = jwt.decode(
            refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        if payload.get("type") != "refresh":
            return InvalidSignatureError

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    except InvalidTokenError:
        raise credentials_exception

    user: Users = await get_user(session=session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


def create_refresh_token(data: dict) -> str:
    """
    Генерация refresh токена

    Args:
        data: Словарь содержащий данные о пользователе и типе токена

    Returns:
        Refresh токен
    """

    to_encode: dict = data.copy()

    if REFRESH_TOKEN_EXPIRE_DAYS:
        expire: datetime = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    else:
        expire: datetime = datetime.now(timezone.utc) + timedelta(days=7)

    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
