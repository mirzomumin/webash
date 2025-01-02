import jwt

from uuid import UUID
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.exceptions import (
    TokenExpired,
    TokenInvalid,
)
from src.users.repository import UserRepository
from src.users.models import User
from src.config import settings


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class JWTAuthentication:
    @classmethod
    async def verify(
        cls,
        *,
        token: Annotated[str, Depends(oauth2_scheme)],
        session: AsyncSession = Depends(get_session),
    ) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: UUID = payload.get("user_id")
            if user_id is None:
                raise TokenInvalid
        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.PyJWTError:
            raise TokenInvalid

        users = await UserRepository.list(db=session, filters=[User.id == user_id])
        return users[0]
