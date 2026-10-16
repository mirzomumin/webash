import time

import jwt
import pytest

from src.config import settings
from src.core.base.token import ACCESS_TOKEN, REFRESH_TOKEN, JWTToken


def test_tokens_have_type_claim():
    tokens = JWTToken.tokens(payload={"sub": "user", "user_id": "id"})

    access = JWTToken.decode_jwt(token=tokens["access"], token_type=ACCESS_TOKEN)
    refresh = JWTToken.decode_jwt(token=tokens["refresh"], token_type=REFRESH_TOKEN)

    assert access["type"] == ACCESS_TOKEN
    assert refresh["type"] == REFRESH_TOKEN


@pytest.mark.parametrize(
    "token_key,expected_type",
    [("access", REFRESH_TOKEN), ("refresh", ACCESS_TOKEN)],
)
def test_decode_jwt_rejects_wrong_type(token_key, expected_type):
    tokens = JWTToken.tokens(payload={"sub": "user", "user_id": "id"})

    with pytest.raises(jwt.InvalidTokenError):
        JWTToken.decode_jwt(token=tokens[token_key], token_type=expected_type)


def test_decode_jwt_rejects_token_without_type():
    # Tokens issued before the type claim existed
    payload = {"sub": "user", "user_id": "id", "exp": time.time() + 60}
    untyped = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    with pytest.raises(jwt.InvalidTokenError):
        JWTToken.decode_jwt(token=untyped, token_type=ACCESS_TOKEN)


def test_encode_jwt_does_not_mutate_payload():
    payload = {"sub": "user", "user_id": "id"}

    JWTToken.tokens(payload=payload)

    assert payload == {"sub": "user", "user_id": "id"}
