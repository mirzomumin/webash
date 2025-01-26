import pytest
from tests.utils import create_user
from src.core.base.token import JWTToken


@pytest.mark.asyncio(loop_scope="session")
async def test_me_success(client):
    user = await create_user()
    payload = {"sub": user.username, "user_id": str(user.id)}
    tokens = JWTToken.tokens(payload=payload)

    response = await client.get(
        "/api/v1/user/me",
        headers={"Authorization": f'Bearer {tokens['access']}'},
    )

    response_data = response.json()

    user_data = response_data["user"]
    ######### assert response ##########
    assert response.status_code == 200
    assert user_data["id"] == str(user.id)
    assert user_data["tid"] == user.tid
    assert user_data["first_name"] == user.first_name
    assert user_data["last_name"] == user.last_name
    assert user_data["username"] == user.username
    assert user_data["is_bot"] == user.is_bot
    assert user_data["created_at"] == user.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_me_fail_invalid_token(client):
    # send request to update tokens
    response = await client.get(
        "/api/v1/user/me",
        headers={"Authorization": "Bearer invalid-access-token"},
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 401
    assert response_data["detail"] == "Token Invalid"
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_me_fail_expired_token(client):
    user = await create_user()
    payload = {"sub": user.username, "user_id": str(user.id)}
    access_token = JWTToken.encode_jwt(payload=payload, ttl=-1)

    # send request to update tokens
    response = await client.get(
        "/api/v1/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 401
    assert response_data["detail"] == "Token Expired"
    ####################################
