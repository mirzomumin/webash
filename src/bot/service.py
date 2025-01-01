from datetime import datetime, timedelta, timezone
from aiogram.types.user import User as TelegramUser  # import telegram User schema
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ObjectAlreadyExists
from src.users.models import Code
from src.users.repository import UserRepository, CodeRepository
from src.users.service import AddUserSchema
from src.utils import get_random_number
from src.database import get_db


class BotService:
    @classmethod
    async def get_auth_code(cls, *, user: TelegramUser) -> int:
        async with get_db() as db:
            try:
                user = await cls._get_or_create_user(user=user, db=db)
                code = await cls._generate_auth_code(user=user, db=db)
                await db.commit()
            except:
                await db.rollback()
                raise

            await db.refresh(code)
        return code.value

    @classmethod
    async def _get_or_create_user(
        cls,
        *,
        user: TelegramUser,
        db: AsyncSession,
    ):
        user_data = await AddUserSchema.to_db(user)
        user = await UserRepository.get(db=db, tid=user_data["tid"])
        if user is None:
            user = await UserRepository.add(db=db, values=user_data)

        return user

    @classmethod
    async def _generate_auth_code(cls, user: TelegramUser, db: AsyncSession):
        filters = [
            Code.expiry >= datetime.now(timezone.utc),
            Code.is_used == False,  # noqa E712
            Code.user_id == user.id,
        ]
        code = await CodeRepository.list(
            db=db,
            filters=filters,
        )

        if code:
            raise ObjectAlreadyExists

        rand_num = get_random_number()
        params = {
            "value": rand_num,
            "user_id": user.id,
            "expiry": datetime.now(timezone.utc) + timedelta(minutes=1),
        }
        code = await CodeRepository.add(db=db, values=params)
        return code
