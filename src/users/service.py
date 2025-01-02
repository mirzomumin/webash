import jwt

from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, Body
from fastapi.security import OAuth2PasswordBearer
from src.database import get_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import (
    CodeInvalidOrExpired,
    ObjectAlreadyExists,
    TokenExpired,
    TokenInvalid,
)
from src.users.repository import UserRepository, CodeRepository
from src.users.schemas import AddUserSchema, OtpData, RefreshToken
from src.users.models import User, Code
from src.config import settings
from src.utils import get_token_details

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserService:
    @classmethod
    async def add(
        cls,
        *,
        user_schema: AddUserSchema,
        session: AsyncSession = Depends(get_session),
    ) -> User:
        user_dict = user_schema.model_dump()
        try:
            new_user = await UserRepository.add(db=session, values=user_dict)
        except IntegrityError:
            raise ObjectAlreadyExists
        await session.commit()
        await session.refresh(new_user)
        return new_user


class AuthService:
    @classmethod
    async def token(
        cls,
        *,
        otp_data: OtpData = Body(...),
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        user: User = await cls._verify_auth_code(
            otp_code=otp_data.otp_code, session=session
        )
        username: str | None = user.username
        user_id: UUID = user.id

        token_details = get_token_details(
            payload={"sub": username, "user_id": str(user_id)}
        )
        return {"token": token_details}

    @classmethod
    async def refresh(
        cls,
        *,
        refresh_token: RefreshToken = Body(...),
    ) -> dict:
        try:
            # Decode the refresh token
            payload = jwt.decode(
                refresh_token.refresh,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            if payload.get("user_id") is None:
                raise TokenInvalid

            # Generate token details
            token_details = get_token_details(payload=payload)
            return {"token": token_details}
        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.PyJWTError:
            raise TokenInvalid

    @classmethod
    async def verify(
        cls,
        *,
        token: str = Depends(oauth2_scheme),
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

    @classmethod
    async def _verify_auth_code(cls, *, otp_code: int, session: AsyncSession) -> User:
        filters = [
            Code.value == otp_code,
            Code.expiry >= datetime.now(timezone.utc),
            Code.is_used == False,  # noqa E712
        ]
        codes = await CodeRepository.list(db=session, filters=filters)

        if len(codes) == 0:
            raise CodeInvalidOrExpired

        code = codes[0]
        return code.user
