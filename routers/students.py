
import asyncio
from io import BytesIO
from typing import Literal

import cloudinary.uploader
import cloudinary_config

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    Query,
    UploadFile,
    File,
)
from sqlmodel import Session, select

from database import (
    Student,
    Course,
    StudentCourse,
    get_session,
)
from schemas import StudentCreate
from exceptions import StudentNotFoundError


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


def log_student_created(student_id: int):
    print(f"Student {student_id} was created")


# =====================================
# CREATE STUDENT
# =====================================

@router.post(
    "/",
    summary="Create a student",
    description="Create a new student and schedule a background logging task."
)
def create_student(
    student_data: StudentCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
):
    student = Student(**student_data.model_dump())

    session.add(student)
    session.commit()
    session.refresh(student)

    background_tasks.add_task(
        log_student_created,
        student.id
    )

    return student


# =====================================
# GET ALL STUDENTS + FILTER + SEARCH
# + SORT + PAGINATION
# =====================================

@router.get("/")
def get_students(
    course: str | None = None,
    search: str | None = None,
    sort_by: Literal["id", "name", "age", "course"] = "id",
    order: Literal["asc", "desc"] = "asc",
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    statement = select(Student)

    # Filter by course
    if course:
        student_ids = (
            select(StudentCourse.student_id)
            .join(
                Course,
                StudentCourse.course_id == Course.id
            )
            .where(Course.name.ilike(f"%{course}%"))
        )

        statement = statement.where(
            Student.id.in_(student_ids)
        )

    # Search by student name
    if search:
        statement = statement.where(
            Student.name.ilike(f"%{search}%")
        )

    # Sort by course
    course_sort = (
        select(Course.name)
        .join(
            StudentCourse,
            StudentCourse.course_id == Course.id
        )
        .where(StudentCourse.student_id == Student.id)
        .order_by(Course.name.asc())
        .limit(1)
        .correlate(Student)
        .scalar_subquery()
    )

    sort_columns = {
        "id": Student.id,
        "name": Student.name,
        "age": Student.age,
        "course": course_sort,
    }

    sort_column = sort_columns[sort_by]

    if order == "desc":
        statement = statement.order_by(sort_column.desc())
    else:
        statement = statement.order_by(sort_column.asc())

    statement = statement.offset(skip).limit(limit)

    return session.exec(statement).all()


# =====================================
# GET ONE STUDENT
# =====================================

@router.get(
    "/{student_id}",
    summary="Get student by ID",
    description="Retrieve a single student using their unique student ID."
)
def get_student(
    student_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if student is None:
        raise StudentNotFoundError(student_id)

    return student


# =====================================
# UPDATE STUDENT
# =====================================

@router.put(
    "/{student_id}",
    summary="Update student",
    description="Update an existing student's information using their ID."
)
def update_student(
    student_id: int,
    updated_student: Student,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    student.name = updated_student.name
    student.age = updated_student.age
    student.profile_photo = updated_student.profile_photo

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


# =====================================
# DELETE STUDENT
# =====================================

@router.delete(
    "/{student_id}",
    summary="Delete student",
    description="Delete an existing student using their unique student ID."
)
def delete_student(
    student_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    session.delete(student)
    session.commit()

    return {
        "message": "Student deleted successfully"
    }


# =====================================
# UPLOAD STUDENT PHOTO - CLOUDINARY
# =====================================

@router.post(
    "/{student_id}/photo",
    summary="Upload student photo",
    description="Upload or update a student's profile photo using Cloudinary."
)
async def upload_student_photo(
    student_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Validate image type
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and WebP images are allowed"
        )

    contents = await file.read()

    # Maximum upload size: 5 MB
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 5 MB"
        )

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            BytesIO(contents),
            folder="student_profiles",
            resource_type="image",
        )

        student.profile_photo = result["secure_url"]

        session.add(student)
        session.commit()
        session.refresh(student)

        return {
            "message": "Student photo uploaded successfully",
            "student_id": student.id,
            "photo_url": student.profile_photo,
        }

    except Exception:
        session.rollback()

        raise HTTPException(
            status_code=502,
            detail="Photo upload failed. Please try again."
        )

    finally:
        await file.close()
