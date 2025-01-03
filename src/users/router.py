from fastapi import APIRouter, Depends

from src.base.utils.auth import jwt_authentication
from src.users.models import User
from src.users.schemas import TokensRsp, GetUserSchema
from src.users.service import AuthService


router = APIRouter()


@router.post("/token")
async def make_token(
    tokens: TokensRsp = Depends(AuthService.token),
) -> TokensRsp:
    return tokens


@router.post("/token/refresh")
async def refresh_token(
    tokens: TokensRsp = Depends(AuthService.refresh),
) -> TokensRsp:
    return tokens


@router.get("/me")
async def get_user(
    user: User = Depends(jwt_authentication),
) -> GetUserSchema:
    return {"user": user}
