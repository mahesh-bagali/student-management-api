
import os
from dotenv import load_dotenv

load_dotenv()

# =====================================
# SECURITY
# =====================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY is missing from .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# =====================================
# DATABASE CONFIGURATION
# =====================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env file")

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Synchronous PostgreSQL URL - Psycopg 3
SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+psycopg://",
    1,
).replace(
    "postgres://",
    "postgresql+psycopg://",
    1,
)


# Asynchronous PostgreSQL URL - asyncpg
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+psycopg://",
    "postgresql+asyncpg://",
    1,
).replace(
    "postgresql+psycopg2://",
    "postgresql+asyncpg://",
    1,
).replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
).replace(
    "postgres://",
    "postgresql+asyncpg://",
    1,
)
