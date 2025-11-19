from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def auth():
    return {"Message": "You gave accessed the auth route", "auth": False}