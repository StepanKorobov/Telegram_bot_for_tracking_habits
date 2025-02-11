from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int
    username: str
    telegram_id: str
    is_active: bool | None = None


class UserInDB(User):
    hashed_password: str


class UserIn(BaseModel):
    username: str = Field(
        ...,
        description="Username in telegram.",
        max_length=64,
    )
    telegram_id: int = Field(
        ...,
        description="Telegram id of the user.",
    )
    password: str = Field(
        ...,
        description="Password for API.",
        max_length=100,
    )


class UserOut(UserIn):
    id: int


class UserTID(BaseModel):
    telegram_id: int
