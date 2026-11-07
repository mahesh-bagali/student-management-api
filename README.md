# Student Management API

A feature-rich REST API built with **FastAPI, Python, PostgreSQL and SQLModel** for managing students, courses and user authentication.

## Features

- Student CRUD operations
- Course CRUD operations
- Student-course many-to-many relationships
- JWT authentication and refresh tokens
- Role-based authorization
- Student search, filtering, sorting and pagination
- Student photo uploads
- Static file serving
- Async database operations
- Background tasks
- Middleware and request logging
- Rate limiting
- WebSocket support
- Database migrations with Alembic
- Automated testing with Pytest

## Tech Stack

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Pydantic
- JWT
- Alembic
- Pytest
- Uvicorn

## Project Structure

```text
fastapi/
├── alembic/
├── dependencies/
├── routers/
├── services/
├── uploads/
├── main.py
├── database.py
├── async_database.py
├── config.py
├── exceptions.py
├── schemas.py
├── security.py
├── rate_limiter.py
├── alembic.ini
├── pytest.ini
└── test_*.py
```

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the server, visit:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

## Testing

Run the automated test suite:

```bash
pytest -v
```

Current test status: **25 tests passed**.

## Project Status

Core API development and integration testing completed. Final cleanup, GitHub preparation and deployment are in progress.

## Author

**Mahesh Bagali**

GitHub: [mahesh-bagali](https://github.com/mahesh-bagali)
