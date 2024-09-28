from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/user")
async def user_me():
    return {"message": "Hello World"}