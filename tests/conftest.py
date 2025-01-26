import logging
import pytest
from asyncpg.exceptions import InvalidCatalogNameError
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from urllib.parse import urlparse, urlunparse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.core.database import get_session, get_db
from src.core.base.models import Base
from src.config import settings

logger = logging.getLogger("webashapp")
engine = create_async_engine(settings.TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


####################### Set Up Test Database ########################


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    parsed_url = urlparse(settings.TEST_DB_URL)
    db_name = parsed_url.path.lstrip("/")
    admin_url = urlunparse(
        parsed_url._replace(path="/postgres")
    )  # Use 'postgres' as the fallback database

    admin_engine = create_async_engine(
        admin_url, isolation_level="AUTOCOMMIT", echo=False
    )

    try:
        # Try creating a connection to the test database
        async with engine.begin() as conn:
            pass
    except (InvalidCatalogNameError, OperationalError):
        # Database does not exist; create it
        async with admin_engine.connect() as admin_conn:
            await admin_conn.execute(text(f'CREATE DATABASE "{db_name}";'))
            logger.info(f"Test database '{db_name}' created.")
    except Exception as e:
        logger.error(f"CONNECTION TO DATABASE ERROR: {e}")

    # Proceed with initializing the test database schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup: Drop the test database
    async with admin_engine.connect() as admin_conn:  # No transaction
        # Terminate all connections to the database before dropping it
        await admin_conn.execute(
            text(
                f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid();
            """
            )
        )
        await admin_conn.execute(text(f'DROP DATABASE "{db_name}";'))
        logger.info(f"Test database '{db_name}' deleted.")

    await admin_engine.dispose()


#####################################################################


############ Override app db sessions ############
async def get_test_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session for tests.
    """
    async with TestSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session context manager for tests.
    """
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
app.dependency_overrides[get_db] = get_test_db

##############################################


@pytest.fixture
async def client():
    """
    Provide an HTTP client for testing.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
