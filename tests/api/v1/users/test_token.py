import pytest
from tests.utils import create_code, create_user


@pytest.mark.asyncio(loop_scope="session")
async def test_token_success(client):
    test_user = await create_user()
    test_code = await create_code(user=test_user)
    response = await client.post(
        "/api/v1/user/token", json={"otp_code": test_code.value}
    )

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 200
    assert "tokens" in response_data
    assert "access" in response_data["tokens"]
    assert "refresh" in response_data["tokens"]
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_fail_invalid_or_expired_code(client):
    response = await client.post("/api/v1/user/token", json={"otp_code": 123456})

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 400
    assert response_data["detail"] == "Invalid or expired code"
    ###################################


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "otp_code,expected_msg",
    [
        (12345, "Input should be greater than or equal to 100000"),
        (1234567, "Input should be less than or equal to 999999"),
        (None, "Input should be a valid integer"),
    ],
)
async def test_token_fail_validation_error(client, otp_code, expected_msg):
    response = await client.post("/api/v1/user/token", json={"otp_code": otp_code})

    response_data = response.json()

    ######### assert response ##########
    assert response.status_code == 422
    assert response_data["detail"][0]["msg"] == expected_msg
    ####################################
