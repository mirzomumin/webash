import jwt
import time
from src.config import settings
from src.api.v1.schemas.user import Tokens

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


class JWTToken:
    @classmethod
    def encode_jwt(cls, *, payload: dict, ttl: int, token_type: str) -> str:
        """Encode and return JWT token"""
        claims = {**payload, "type": token_type, "exp": time.time() + ttl}
        encoded_jwt = jwt.encode(
            claims,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        return encoded_jwt

    @classmethod
    def decode_jwt(cls, *, token: str, token_type: str) -> dict:
        """Decode JWT token and return payload"""
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != token_type:
            raise jwt.InvalidTokenError("Unexpected token type")
        return payload

    @classmethod
    def tokens(cls, *, payload: dict) -> Tokens:
        """Return access and refresh tokens"""

        access_token = cls.encode_jwt(
            payload=payload,
            ttl=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            token_type=ACCESS_TOKEN,
        )
        refresh_token = cls.encode_jwt(
            payload=payload,
            ttl=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            token_type=REFRESH_TOKEN,
        )

        return {
            "access": access_token,
            "refresh": refresh_token,
        }
