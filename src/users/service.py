from fastapi import Depends
from src.database import get_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import ObjectAlreadyExists
from src.users.repository import UserRepository
from src.users.schemas import AddUserSchema
from src.users.models import User


class UserService:
    @classmethod
    async def add(
        cls,
        user_schema: AddUserSchema,
        db: AsyncSession = Depends(get_session),
    ) -> User:
        user_dict = user_schema.model_dump()
        try:
            new_user = await UserRepository.add(db=db, values=user_dict)
        except IntegrityError:
            raise ObjectAlreadyExists
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @classmethod
    async def auth(
        cls,
        otp_code: int,
    ):
        pass
