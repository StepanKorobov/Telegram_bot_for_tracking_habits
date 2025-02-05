from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/auth/register")
async def register():
    """
    Регистрация пользователей
    """
    pass


@router.get("/auth/token")
async def user_me() -> JSONResponse:
    return JSONResponse({"message": "Hello World"})


@router.get("/auth/login")
async def user_login():
    return {"message": "Hello World"}


@router.get("/auth/refresh_token")
async def user_register():
    pass
