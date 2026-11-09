# Student Management API

A feature-rich REST API built with **FastAPI, Python, PostgreSQL, and SQLModel** for managing students, courses, and user authentication.

## Features

- Student CRUD operations
- Course CRUD operations
- Student-course many-to-many relationships
- JWT authentication with access and refresh tokens
- Role-based authorization
- Student search, filtering, sorting, and pagination
- Student profile photo uploads using Cloudinary
- Asynchronous database operations
- Background tasks
- Middleware and request logging
- CORS configuration
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
- JWT Authentication
- Alembic
- Cloudinary
- Pytest
- Uvicorn
- Docker
- Docker Compose
- Git and GitHub

## Project Structure

```text
fastapi/
├── alembic/
├── dependencies/
├── routers/
├── services/
├── main.py
├── database.py
├── async_database.py
├── config.py
├── cloudinary_config.py
├── exceptions.py
├── schemas.py
├── security.py
├── rate_limiter.py
├── Dockerfile
├── .dockerignore
├── compose.yaml
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── test_*.py
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/mahesh-bagali/student-management-api.git
cd student-management-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root and configure the required database, authentication, and Cloudinary credentials.

Never commit your `.env` file to GitHub.

### 6. Start the application

```bash
uvicorn main:app --reload
```

## Running with Docker Compose

### Prerequisites

- Docker Desktop
- Docker Compose

Make sure your `.env` file is configured before starting.

### Build and start containers

```bash
docker compose up -d --build
```

### Check running containers

```bash
docker compose ps
```

### View application logs

```bash
docker compose logs -f api
```

### Stop and remove containers

```bash
docker compose down
```

## API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, visit:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- OpenAPI Schema: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Testing

Run the automated test suite:

```bash
pytest -v
```

**Current test status: 25 tests passed.**

## Deployment

The application is deployed using:

- **Render:** FastAPI application hosting
- **Neon PostgreSQL:** Cloud database
- **Cloudinary:** Student profile photo storage

## Project Links

- GitHub Repository: [https://github.com/mahesh-bagali/student-management-api](https://github.com/mahesh-bagali/student-management-api)
- Live API: [https://student-management-api-tabs.onrender.com](https://student-management-api-tabs.onrender.com)
- Live API Documentation:[https://student-management-api-tabs.onrender.com](https://student-management-api-tabs.onrender.com)/docs

## Project Status

Core development, automated testing, cloud deployment, Docker containerization, and Docker Compose configuration completed.

## Author

**Mahesh Bagali**

GitHub: [https://github.com/mahesh-bagali](https://github.com/mahesh-bagali)
