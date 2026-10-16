import jwt

from datetime import datetime, timezone
from uuid import UUID
from fastapi import Depends, Body

from src.api.v1.schemas.user import (
    AddUserSchema,
    OtpData,
    RefreshToken,
)
from src.core.database import get_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.base.exceptions import (
    CodeInvalidOrExpired,
    ObjectAlreadyExists,
    TokenExpired,
    TokenInvalid,
)
from src.core.repositories.user import UserRepository, CodeRepository
from src.core.models.user import User, Code
from src.core.base.token import REFRESH_TOKEN, JWTToken


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
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        try:
            # Decode the refresh token
            payload = JWTToken.decode_jwt(
                token=refresh_token.refresh,
                token_type=REFRESH_TOKEN,
            )
            user_id = UUID(payload["user_id"])

        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except (jwt.PyJWTError, KeyError, TypeError, ValueError):
            raise TokenInvalid

        users = await UserRepository.list(db=session, filters=[User.id == user_id])
        if not users:
            raise TokenInvalid
        user = users[0]

        # Get tokens
        payload = {"sub": user.username, "user_id": str(user.id)}
        tokens = JWTToken.tokens(payload=payload)
        return {"tokens": tokens}

    @classmethod
    async def _verify_auth_code(cls, *, otp_code: int, session: AsyncSession) -> User:
        """Consume an active code and return its owner. A code works only once."""
        filters = [
            Code.value == otp_code,
            Code.expiry >= datetime.now(timezone.utc),
            Code.is_used == False,  # noqa E712
        ]
        codes = await CodeRepository.list(db=session, filters=filters)

        if len(codes) == 0:
            raise CodeInvalidOrExpired

        user = codes[0].user
        for code in codes:
            code.is_used = True
        await session.commit()

        # Active codes are generated unique, so a duplicate means a race between
        # two generations. Its owner is ambiguous: burn every copy instead.
        if len(codes) > 1:
            raise CodeInvalidOrExpired

        await session.refresh(user)
        return user
