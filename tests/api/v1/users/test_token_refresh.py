import pytest
from tests.utils import create_user
from src.core.utils.token import JWTToken


@pytest.mark.asyncio(loop_scope="session")
async def test_token_refresh_success(client):
    user = await create_user()
    payload = {"sub": user.username, "user_id": str(user.id)}
    tokens = JWTToken.tokens(payload=payload)

    # send request to update tokens
    response = await client.post(
        "/api/v1/user/token-refresh", json={"refresh": tokens["refresh"]}
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 200
    assert "tokens" in response_data
    assert "access" in response_data["tokens"]
    assert "refresh" in response_data["tokens"]
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_refresh_fail_invalid(client):
    # send request to update tokens
    response = await client.post(
        "/api/v1/user/token-refresh", json={"refresh": "invalid-refresh-token"}
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 401
    assert response_data["detail"] == "Token Invalid"
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_refresh_fail_expired(client):
    user = await create_user()
    payload = {"sub": user.username, "user_id": str(user.id)}
    refresh_token = JWTToken.encode_jwt(payload=payload, ttl=-1)

    # send request to update tokens
    response = await client.post(
        "/api/v1/user/token-refresh", json={"refresh": refresh_token}
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 401
    assert response_data["detail"] == "Token Expired"
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_refresh_fail_validation_error(client):
    # send request to update tokens
    response = await client.post("/api/v1/user/token-refresh", json={"refresh": None})

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 422
    assert response_data["detail"][0]["msg"] == "Input should be a valid string"
    ####################################
