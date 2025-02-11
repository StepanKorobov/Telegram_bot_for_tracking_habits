import sys
import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from shemas.shema import User, UserInDB, Token, TokenData, UserIn, UserOut
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import sessions
from database.models import check_user_exist, write_user

SECRET_KEY = "29f9d7c10178d852330fa3b08119de20cabe644b8403c022c16ce750e1a51dc3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# class TelegramOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
#     def __init__(
#         self,
#         username: str = Form(...),
#         password: str = Form(...),
#         telegram_id: int = Form(...),
#         grant_type: str = Form(default=None, regex="password"),
#         scope: str = Form(default=""),
#         client_id: Optional[str] = Form(default=None),
#         client_secret: Optional[str] = Form(default=None),
#     ):
#         super().__init__(
#             grant_type=grant_type,
#             username=username,
#             password=password,
#             scope=scope,
#             client_id=client_id,
#             client_secret=client_secret,
#         )
#         self.telegram_id = telegram_id


router = APIRouter()

fake_users_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "telegram_id": "124",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "is_active": True,
    }
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/auth/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Данный эндпоинт принимает логин и пароль, возвращая token
    :param form_data:
    :return:
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print(form_data.password, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# async def user_login(current_user: Annotated[User, Depends(get_current_user)]):
@router.post("/auth/login")
async def user_login(user_data: UserIn,
                     session: AsyncSession = Depends(sessions)
                     ):
    """
    Эндпоинт Для регистрации пользователей
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


@router.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
