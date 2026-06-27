from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(
        ...,
        title="Username",
        description="Username in telegram.",
        max_length=64,
    )
    telegram_id: int = Field(
        ...,
        title="Telegram ID",
        gt=0,
        description="Telegram id of the user.",
    )


class UserIn(UserBase):
    password: str = Field(
        ...,
        title="Password",
        description="Password for API.",
        max_length=100,
    )


class UserOut(UserBase):
    id: int = Field(
        ...,
        title="ID from db",
        gt=0,
        description="unique user ID",
    )


class User(UserOut):
    # id: int
    is_active: bool | None = Field(
        ...,
        title="Is active",
        description="Is active user",
    )

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    username: str | None = Field(
        ...,
        title="Username",
        description="Username in telegram.",
    )


class TokenOut(BaseModel):
    access_token: str = Field(
        ...,
        title="Access Token",
        description="Access token",
    )
    refresh_token: str = Field(
        ...,
        title="Refresh Token",
        description="Refresh token",
    )
    token_type: str = Field(
        ...,
        title="Token Type",
        description="Token Type, сейчас только Bearer",
    )


class RefreshToken(BaseModel):
    refresh_token: str = Field(
        ...,
        title="Refresh Token",
        description="Refresh token пользователя",
    )


# class UserInDB(User):
#     password: str
#
#
# class UserTID(BaseModel):
#     telegram_id: int
