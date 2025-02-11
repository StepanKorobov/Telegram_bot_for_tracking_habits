from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    telegram_id: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserInDB(User):
    hashed_password: str
