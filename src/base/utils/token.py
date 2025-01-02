import jwt
from datetime import datetime, timezone, timedelta
from src.config import settings
from src.users.schemas import TokenDetails


class JWTToken:
    @classmethod
    async def create_jwt_token(
        cls, *, payload: dict, expires_delta: timedelta | None = None
    ):
        """Create JWT token"""
        expire = datetime.now(timezone.utc) + expires_delta
        payload.update({"exp": expire})
        encoded_jwt = jwt.encode(
            payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @classmethod
    async def get_token_details(cls, *, payload: dict) -> TokenDetails:
        """Return token details (access, refresh, type)"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        access_token = await cls.create_jwt_token(
            payload=payload,
            expires_delta=access_token_expires,
        )
        refresh_token = await cls.create_jwt_token(
            payload=payload,
            expires_delta=refresh_token_expires,
        )

        return {
            "access": access_token,
            "refresh": refresh_token,
            "type": "bearer",
        }

    @classmethod
    async def get_payload(cls, *, token: str) -> dict:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
