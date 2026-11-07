
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from config import SYNC_DATABASE_URL


# =====================================
# DATABASE MODELS
# =====================================

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    password_hash: str
    role: str = "user"


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str


class StudentCourse(SQLModel, table=True):
    student_id: int = Field(
        foreign_key="student.id",
        primary_key=True
    )
    course_id: int = Field(
        foreign_key="course.id",
        primary_key=True
    )


class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int
    profile_photo: str | None = None

    courses: list["Course"] = Relationship(
        back_populates="students",
        link_model=StudentCourse
    )


class Course(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    students: list["Student"] = Relationship(
        back_populates="courses",
        link_model=StudentCourse
    )


# =====================================
# DATABASE ENGINE
# =====================================

engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False
)


# =====================================
# DATABASE SESSION
# =====================================

def get_session():
    with Session(engine) as session:
        yield session
