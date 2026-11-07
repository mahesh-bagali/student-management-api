
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env file")

# Convert PostgreSQL URL to asyncpg URL
ASYNC_DATABASE_URL = DATABASE_URL

ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
    "postgresql+psycopg://",
    "postgresql+asyncpg://",
    1,
)

ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
    "postgresql+psycopg2://",
    "postgresql+asyncpg://",
    1,
)

ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
)
