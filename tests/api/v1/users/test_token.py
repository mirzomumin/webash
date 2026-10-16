import pytest
from src.core.models.user import Code
from src.core.repositories.user import CodeRepository
from tests.conftest import get_test_db
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


@pytest.mark.asyncio(loop_scope="session")
async def test_token_fail_code_reused(client):
    test_user = await create_user()
    test_code = await create_code(user=test_user)

    first = await client.post("/api/v1/user/token", json={"otp_code": test_code.value})
    second = await client.post("/api/v1/user/token", json={"otp_code": test_code.value})

    ######### assert response ##########
    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "Invalid or expired code"
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_marks_code_used(client):
    test_user = await create_user()
    test_code = await create_code(user=test_user)

    response = await client.post(
        "/api/v1/user/token", json={"otp_code": test_code.value}
    )

    async with get_test_db() as db:
        codes = await CodeRepository.list(db=db, filters=[Code.id == test_code.id])

    ######### assert response ##########
    assert response.status_code == 200
    assert codes[0].is_used is True
    ####################################


@pytest.mark.asyncio(loop_scope="session")
async def test_token_fail_code_shared_by_two_users(client):
    first_user = await create_user()
    second_user = await create_user()
    first_code = await create_code(user=first_user)
    second_code = await create_code(user=second_user, number=first_code.value)

    response = await client.post(
        "/api/v1/user/token", json={"otp_code": first_code.value}
    )

    async with get_test_db() as db:
        codes = await CodeRepository.list(
            db=db, filters=[Code.id.in_([first_code.id, second_code.id])]
        )

    ######### assert response ##########
    # Owner is ambiguous: nobody is logged in and both copies are burned
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired code"
    assert all(code.is_used for code in codes)
    ####################################
