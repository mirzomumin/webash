import random
import re
import unicodedata
import jwt
from datetime import datetime, timezone, timedelta
from src.config import settings
from src.users.schemas import TokenDetails


def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def get_random_number():
    """Return five digit number"""
    return random.randint(100_000, 999_999)


def create_jwt_token(payload: dict, expires_delta: timedelta | None = None):
    """Create JWT token"""
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire})
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_token_details(payload: dict) -> TokenDetails:
    """Return token details (access, refresh, type)"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_jwt_token(
        payload=payload,
        expires_delta=access_token_expires,
    )
    refresh_token = create_jwt_token(
        payload=payload,
        expires_delta=refresh_token_expires,
    )

    return {
        "access": access_token,
        "refresh": refresh_token,
        "type": "bearer",
    }
