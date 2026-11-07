
import logging
import time
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import Student
from schemas import StudentCreate
from async_database import get_async_session

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from rate_limiter import limiter
from exceptions import StudentNotFoundError

from routers.students import router as students_router
from routers.users import router as users_router

from routers.courses import (
    router as courses_router,
    student_courses_router,
)


# =====================================
# LOGGING
# =====================================

logger = logging.getLogger(__name__)


# =====================================
# LIFESPAN
# =====================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application is starting...")

    yield

    print("Application is shutting down...")


# =====================================
# FASTAPI APPLICATION
# =====================================

app = FastAPI(
    lifespan=lifespan,
    title="Student Management API",
    description="REST API for managing students, users, courses and enrollments.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# =====================================
# HOME ROUTE
# =====================================

@app.get("/")
async def home():
    return {
        "message": "Student Management API is running successfully"
    }


# =====================================
# REGISTER ROUTERS
# =====================================

app.include_router(students_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(student_courses_router)


# =====================================
# CUSTOM EXCEPTION HANDLER
# =====================================

@app.exception_handler(StudentNotFoundError)
async def student_not_found_handler(
    request: Request,
    exc: StudentNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


# =====================================
# GLOBAL EXCEPTION HANDLER
# =====================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception("Unexpected error occurred")

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# =====================================
# MIDDLEWARE
# =====================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    print(
        f"{request.method} {request.url.path} - "
        f"{process_time:.4f}s"
    )

    return response


# =====================================
# RATE LIMITING
# =====================================

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# STATIC FILES
# =====================================

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# =====================================
# WEBSOCKET
# =====================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()

            await websocket.send_text(
                f"Server received: {message}"
            )

    except WebSocketDisconnect:
        print("Client disconnected")


# =====================================
# ASYNC DEMO
# =====================================

@app.get("/async-demo")
async def async_demo():
    return {
        "message": "My first async FastAPI route"
    }


# =====================================
# ASYNC DATABASE TEST
# =====================================

@app.get("/async-db-test")
async def async_db_test(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(text("SELECT 1"))

    return {
        "message": "Async database connected",
        "result": result.scalar(),
    }


# =====================================
# GET ALL STUDENTS ASYNC
# =====================================

@app.get("/async-students")
async def get_students_async(
    session: AsyncSession = Depends(get_async_session),
):
    statement = select(Student)

    result = await session.execute(statement)

    students = result.scalars().all()

    return students


# =====================================
# GET STUDENT BY ID ASYNC
# =====================================

@app.get("/async-students/{student_id}")
async def get_student_async(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    statement = select(Student).where(
        Student.id == student_id
    )

    result = await session.execute(statement)

    student = result.scalars().first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    return student


# =====================================
# CREATE STUDENT ASYNC
# =====================================

@app.post("/async-students")
async def create_student_async(
    student_data: StudentCreate,
    session: AsyncSession = Depends(get_async_session),
):
    new_student = Student(
        name=student_data.name,
        age=student_data.age,
        profile_photo=student_data.profile_photo,
    )

    session.add(new_student)

    await session.commit()
    await session.refresh(new_student)

    return new_student


# =====================================
# UPDATE STUDENT ASYNC
# =====================================

@app.put("/async-students/{student_id}")
async def update_student_async(
    student_id: int,
    student_data: StudentCreate,
    session: AsyncSession = Depends(get_async_session),
):
    student = await session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    student.name = student_data.name
    student.age = student_data.age
    student.profile_photo = student_data.profile_photo

    session.add(student)

    await session.commit()
    await session.refresh(student)

    return student


# =====================================
# DELETE STUDENT ASYNC
# =====================================

@app.delete("/async-students/{student_id}")
async def delete_student_async(
    student_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    student = await session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    await session.delete(student)
    await session.commit()

    return {
        "message": "Student deleted successfully"
    }
