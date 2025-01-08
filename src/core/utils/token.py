import jwt
import time
from src.config import settings
from src.core.schemas.user import Tokens


class JWTToken:
    @classmethod
    def encode_jwt(cls, *, payload: dict, ttl: int) -> str:
        """Encode and return JWT token"""
        expires = time.time() + ttl
        payload["exp"] = expires
        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt

    @classmethod
    def decode_jwt(cls, *, token: str) -> dict:
        """Decode JWT token and return payload"""
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    @classmethod
    def tokens(cls, *, payload: dict) -> Tokens:
        """Return access and refresh tokens"""

        access_token = cls.encode_jwt(
            payload=payload,
            ttl=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        )
        refresh_token = cls.encode_jwt(
            payload=payload,
            ttl=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )

        return {
            "access": access_token,
            "refresh": refresh_token,
        }
