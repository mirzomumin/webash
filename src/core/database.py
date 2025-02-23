from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)
from src.config import settings


async_engine = create_async_engine(
    settings.DB_URL,
    pool_timeout=30,  # Increase the timeout
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_size=10,  # Number of connections to keep open
    max_overflow=5,  # Number of connections to create beyond the pool_size
)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Return db session within async generator.
    Used only in fastapi app.
    """
    async with SessionLocal() as session:
        yield session


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Return db session within async context manager.
    Used only in bot.
    """
    async with SessionLocal() as session:
        yield session
