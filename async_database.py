from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from config import ASYNC_DATABASE_URL

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session


async def test_async_connection():
 async with async_engine.connect() as connection:
        result = await connection.exec_driver_sql("SELECT 1")
        print("Async PostgreSQL connected:", result.scalar())


async def get_async_database_version():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT version()")
        )
        return result.scalar()

async def close_async_database():
    await async_engine.dispose()