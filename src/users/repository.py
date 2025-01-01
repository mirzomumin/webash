from sqlalchemy import insert, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument
from src.users.models import User, Code


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


class CodeRepository:
    @classmethod
    async def add(
        cls,
        *,
        db: AsyncSession,
        values: dict,
    ) -> Code:
        stmt = insert(Code).values(**values).returning(Code)
        result = await db.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def list(
        cls,
        *,
        db: AsyncSession,
        filters: list[_ColumnExpressionArgument[bool]] = [],
    ) -> list[Code]:
        query = select(Code).where(and_(*filters))
        result = await db.execute(query)
        return result.scalars().all()
