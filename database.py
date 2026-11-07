from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

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
    age:int
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


postgres_url = os.getenv("DATABASE_URL")

if not postgres_url:
    raise ValueError("DATABASE_URL is missing from .env file")

engine = create_engine(postgres_url)
#SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session