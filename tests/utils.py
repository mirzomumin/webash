from uuid import uuid4
from datetime import datetime, timezone, timedelta
from src.core.repositories.user import UserRepository, CodeRepository
from src.core.models.user import User, Code
from src.core.base.funcs import get_random_number
from tests.conftest import get_test_db


async def create_user(
    *,
    tid: int | None = None,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    if tid is None:
        tid = get_random_number()

    if username is None:
        username = uuid4().hex[:6].upper()

    if first_name is None:
        first_name = uuid4().hex[:6].upper()

    if last_name is None:
        last_name = uuid4().hex[:6].upper()

    async with get_test_db() as db:
        user_data = {
            "tid": tid,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "is_bot": False,
            "language_code": "en",
        }
        user = await UserRepository.add(db=db, values=user_data)
        await db.commit()
        await db.refresh(user)
        return user


async def create_code(
    *,
    user: User,
    number: int | None = None,
) -> Code:
    if number is None:
        number = get_random_number()

    code_data = {
        "user_id": user.id,
        "value": number,
        "expiry": datetime.now(timezone.utc) + timedelta(minutes=1),
    }
    async with get_test_db() as db:
        code = await CodeRepository.add(db=db, values=code_data)
        await db.commit()
        await db.refresh(code)
        return code
