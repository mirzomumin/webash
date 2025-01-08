import jwt

from uuid import UUID
from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPBearer
from src.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.utils.exceptions import (
    TokenExpired,
    TokenInvalid,
)
from src.core.repositories.user import UserRepository
from src.core.models.user import User
from src.core.utils.dependencies import get_token
from src.core.utils.token import JWTToken


class JWTAuthentication(HTTPBearer):
    async def __call__(
        self,
        *,
        token: Annotated[str, Depends(get_token)],
        session: AsyncSession = Depends(get_session),
    ) -> User:
        try:
            payload = JWTToken.decode_jwt(token=token)
            user_id: UUID = payload.get("user_id")
            if user_id is None:
                raise TokenInvalid
        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.PyJWTError:
            raise TokenInvalid

        users = await UserRepository.list(db=session, filters=[User.id == user_id])
        return users[0]


jwt_authentication = JWTAuthentication()
