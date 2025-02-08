import sys
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from database.database import sessions, create_tables

router = APIRouter()


@router.post("/auth/register")
async def register():
    """
    Регистрация пользователей
    """
    return {"message": "Hello World"}


@router.get("/auth/login")
async def user_login():
    return {"message": "Hello World"}


@router.get("/auth/token")
async def user_me() -> JSONResponse:
    return JSONResponse({"message": "Hello World"})


@router.get("/auth/refresh_token")
async def user_register():
    pass
