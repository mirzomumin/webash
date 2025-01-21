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
