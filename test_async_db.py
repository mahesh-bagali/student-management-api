
import pytest

from async_database import get_async_database_version


@pytest.mark.asyncio
async def test_async_database_connection():
    version = await get_async_database_version()
    assert version is not None
    print("PostgreSQL version:", version)
