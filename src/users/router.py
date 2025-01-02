from fastapi import APIRouter, Depends

from src.base.utils.auth import JWTAuthentication
from src.users.models import User
from src.users.schemas import Token, GetUserSchema
from src.users.service import AuthService


router = APIRouter()


@router.post("/token")
async def make_token(
    token: Token = Depends(AuthService.token),
) -> Token:
    return token


@router.post("/token/refresh")
async def refresh_token(
    token: Token = Depends(AuthService.refresh),
) -> Token:
    return token


@router.get("/me")
async def get_user(
    user: User = Depends(JWTAuthentication.verify),
) -> GetUserSchema:
    return {"user": user}
