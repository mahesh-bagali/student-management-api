
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.engine import make_url

from config import ASYNC_DATABASE_URL


# Remove parameters unsupported by asyncpg
async_url = make_url(ASYNC_DATABASE_URL)

query_params = dict(async_url.query)
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)

async_url = async_url.set(query=query_params)


# Async PostgreSQL engine
async_engine = create_async_engine(
    async_url,
    echo=False,
    connect_args={"ssl": "require"},
)


# Async session
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
        result = await session.execute(text("SELECT version()"))
        return result.scalar()


async def close_async_database():
    await async_engine.dispose()
