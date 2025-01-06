import jwt

from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, Body
from src.database import get_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.exceptions import (
    CodeInvalidOrExpired,
    ObjectAlreadyExists,
    TokenExpired,
    TokenInvalid,
)
from src.users.repository import UserRepository, CodeRepository
from src.users.schemas import AddUserSchema, OtpData, RefreshToken
from src.users.models import User, Code
from src.base.utils.token import JWTToken


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

        # Get tokens
        payload = {"sub": username, "user_id": str(user_id)}
        tokens = JWTToken.tokens(payload=payload)
        return {"tokens": tokens}

    @classmethod
    async def refresh(
        cls,
        *,
        refresh_token: RefreshToken = Body(...),
    ) -> dict:
        try:
            # Decode the refresh token
            payload = JWTToken.decode_jwt(
                token=refresh_token.refresh,
            )

            if payload.get("user_id") is None:
                raise TokenInvalid

        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.PyJWTError:
            raise TokenInvalid

        # Get tokens
        tokens = JWTToken.tokens(payload=payload)
        return {"token": tokens}

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
