from fastapi import APIRouter, Depends

from src.users.schemas import Token
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
