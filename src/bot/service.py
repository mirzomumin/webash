from datetime import datetime, timedelta, timezone
from aiogram.types.user import User as TelegramUser  # import telegram User schema
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base.exceptions import ObjectAlreadyExists, UserNotFound
from src.core.models.user import Code, User
from src.core.repositories.user import UserRepository, CodeRepository
from src.api.v1.schemas.user import CustomTelegramUser
from src.core.base.funcs import get_random_number
from src.core.database import get_db


class BotService:
    @classmethod
    async def get_passcode(
        cls,
        *,
        telegram_user: TelegramUser,
        phone_number: str | None = None,
    ) -> Code:
        async with get_db() as db:
            try:
                user = await UserRepository.get(db=db, tid=telegram_user.id)
                if user is None and phone_number is None:
                    raise UserNotFound

                if user is None:
                    user = await cls.create_user(
                        telegram_user=telegram_user,
                        phone_number=phone_number,
                        db=db,
                    )
                code = await cls.generate_passcode(user=user, db=db)
                await db.commit()
            except:
                await db.rollback()
                raise

            await db.refresh(code)
            return code

    @classmethod
    async def create_user(
        cls,
        *,
        telegram_user: TelegramUser,
        phone_number: str,
        db: AsyncSession,
    ) -> User:
        user_data = CustomTelegramUser.to_db(
            telegram_user=telegram_user,
            phone_number=phone_number,
        )
        user = await UserRepository.add(db=db, values=user_data)
        return user

    @classmethod
    async def generate_passcode(cls, user: User, db: AsyncSession) -> Code:
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
