from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/auth/token")
async def user_me():
    return {"message": "Hello World"}


@router.get("/auth/login")
async def user_login():
    return {"message": "Hello World"}


@router.get("/auth/refresh_token")
async def user_register():
    pass
