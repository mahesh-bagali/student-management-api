
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import Course, Student, StudentCourse, get_session


# Course router
router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

# Student-Course relationship router
student_courses_router = APIRouter(
    tags=["Courses"]
)


# =====================================
# CREATE COURSE
# =====================================

@router.post(
    "/",
    summary="Create course",
    description="Create a new course in the student management system."
)
def create_course(
    course: Course,
    session: Session = Depends(get_session),
):
    session.add(course)
    session.commit()
    session.refresh(course)

    return course


# =====================================
# GET ALL COURSES
# =====================================

@router.get(
    "/",
    summary="Get all courses",
    description="Retrieve all available courses."
)
def get_courses(
    session: Session = Depends(get_session),
):
    courses = session.exec(select(Course)).all()
    return courses


# =====================================
# ENROLL STUDENT IN COURSE
# =====================================

@student_courses_router.post(
    "/students/{student_id}/courses/{course_id}",
    summary="Enroll student in course",
    description="Connect a student to a course using their IDs."
)
def connect_student_course(
    student_id: int,
    course_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    existing = session.get(
        StudentCourse,
        (student_id, course_id)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Student is already connected to this course"
        )

    student_course = StudentCourse(
        student_id=student_id,
        course_id=course_id
    )

    session.add(student_course)
    session.commit()

    return {"message": "Student connected to Course"}


# =====================================
# REMOVE STUDENT FROM COURSE
# =====================================

@student_courses_router.delete(
    "/students/{student_id}/courses/{course_id}",
    summary="Remove student from course",
    description="Remove a student's enrollment in a course."
)
def disconnect_student_course(
    student_id: int,
    course_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    connection = session.get(
        StudentCourse,
        (student_id, course_id)
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Student is not connected to this course"
        )

    session.delete(connection)
    session.commit()

    return {"message": "Student disconnected from Course"}


# =====================================
# GET STUDENT COURSES
# =====================================

@student_courses_router.get(
    "/students/{student_id}/courses",
    summary="Get student courses",
    description="Retrieve all courses enrolled by a specific student."
)
def get_student_courses(
    student_id: int,
    session: Session = Depends(get_session),
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student.courses


# =====================================
# GET STUDENTS IN A COURSE
# =====================================

@router.get(
    "/{course_id}/students",
    summary="Get course students",
    description="Retrieve all students enrolled in a specific course."
)
def get_course_students(
    course_id: int,
    session: Session = Depends(get_session),
):
    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course.students


# =====================================
# UPDATE COURSE
# =====================================

@router.put(
    "/{course_id}",
    summary="Update course",
    description="Update the name or information of an existing course."
)
def update_course(
    course_id: int,
    course_data: Course,
    session: Session = Depends(get_session),
):
    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    course.name = course_data.name

    session.add(course)
    session.commit()
    session.refresh(course)

    return course


# =====================================
# DELETE COURSE
# =====================================

@router.delete(
    "/{course_id}",
    summary="Delete course",
    description="Delete a course and its student enrollment records."
)
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
):
    course = session.get(Course, course_id)

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    connections = session.exec(
        select(StudentCourse).where(
            StudentCourse.course_id == course_id
        )
    ).all()

    for connection in connections:
        session.delete(connection)

    session.delete(course)
    session.commit()

    return {"message": "Course deleted successfully"}
