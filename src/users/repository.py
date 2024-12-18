from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.models import User


class UserRepository:
    @classmethod
    async def add(cls, *, db: AsyncSession, values: dict) -> User:
        stmt = insert(User).values(**values).returning(User)
        result = await db.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def get(
        cls,
        *,
        tid: int,
        db: AsyncSession,
    ) -> User:
        query = select(User).where(User.tid == tid)
        result = await db.execute(query)
        return result.scalar()
