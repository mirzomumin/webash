from fastapi import APIRouter, Depends

from src.api.v1.schemas.user import TokensRsp, GetUserSchema
from src.api.v1.services.user import AuthService
from src.core.base.auth import jwt_authentication
from src.core.models.user import User


router = APIRouter(prefix="/user")


@router.post("/token")
async def make_token(
    tokens: TokensRsp = Depends(AuthService.token),
) -> TokensRsp:
    return tokens


@router.post("/token-refresh")
async def refresh_token(
    tokens: TokensRsp = Depends(AuthService.refresh),
) -> TokensRsp:
    return tokens


@router.get("/me")
async def get_user(
    user: User = Depends(jwt_authentication),
) -> GetUserSchema:
    return {"user": user}
