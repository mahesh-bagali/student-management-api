
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from main import app
from database import get_session


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    test_engine.dispose()


def create_test_student(client):
    return client.post(
        "/students/",
        json={
            "name": "Rahul",
            "age": 21,
            "profile_photo": None,
        },
    )


def test_create_student(client):
    response = create_test_student(client)

    assert response.status_code == 200
    assert response.json()["name"] == "Rahul"


def test_get_all_students(client):
    create_test_student(client)

    response = client.get("/students/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_student_by_id(client):
    created = create_test_student(client)
    student_id = created.json()["id"]

    response = client.get(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Rahul"


def test_update_student(client):
    created = create_test_student(client)
    student_id = created.json()["id"]

    response = client.put(
        f"/students/{student_id}",
        json={
            "name": "Updated Rahul",
            "age": 22,
            "profile_photo": None,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Rahul"
    assert response.json()["age"] == 22


def test_delete_student(client):
    created = create_test_student(client)
    student_id = created.json()["id"]

    response = client.delete(f"/students/{student_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Student deleted successfully"

    check = client.get(f"/students/{student_id}")
    assert check.status_code == 404


def create_multiple_students(client):
    students = [
        {"name": "Rahul", "age": 21, "profile_photo": None},
        {"name": "Priya", "age": 23, "profile_photo": None},
        {"name": "Amit", "age": 20, "profile_photo": None},
    ]

    for student in students:
        client.post("/students/", json=student)


def test_search_students(client):
    create_multiple_students(client)

    response = client.get("/students/?search=Rahul")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Rahul"


def test_sort_students_by_age(client):
    create_multiple_students(client)

    response = client.get("/students/?sort_by=age&order=asc")

    assert response.status_code == 200

    ages = [student["age"] for student in response.json()]
    assert ages == [20, 21, 23]


def test_sort_students_by_name(client):
    create_multiple_students(client)

    response = client.get("/students/?sort_by=name&order=asc")

    assert response.status_code == 200

    names = [student["name"] for student in response.json()]
    assert names == ["Amit", "Priya", "Rahul"]


def test_student_pagination(client):
    create_multiple_students(client)

    response = client.get("/students/?skip=1&limit=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Priya"


def test_student_search_no_match(client):
    create_multiple_students(client)

    response = client.get("/students/?search=Unknown")

    assert response.status_code == 200
    assert response.json() == []


# =====================================
# CLOUDINARY PHOTO UPLOAD TEST
# =====================================

@patch("cloudinary.uploader.upload")
def test_upload_student_photo(mock_upload, client):
    mock_upload.return_value = {
        "secure_url": (
            "https://res.cloudinary.com/demo/image/upload/"
            "student_profiles/test.jpg"
        )
    }

    created = create_test_student(client)
    student_id = created.json()["id"]

    response = client.post(
        f"/students/{student_id}/photo",
        files={
            "file": (
                "test.jpg",
                b"fake-image-content",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["student_id"] == student_id

    assert response.json()["photo_url"].startswith(
        "https://res.cloudinary.com/"
    )

    mock_upload.assert_called_once()


def test_filter_students_by_course(client):
    # Create student
    student_response = create_test_student(client)
    student_id = student_response.json()["id"]

    # Create course
    course_response = client.post(
        "/courses",
        json={"name": "Python"},
    )
    course_id = course_response.json()["id"]

    # Connect student to course
    connect_response = client.post(
        f"/students/{student_id}/courses/{course_id}"
    )
    assert connect_response.status_code == 200

    # Filter students by course
    response = client.get("/students/?course=Python")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Rahul"


def test_get_all_courses(client):
    client.post("/courses", json={"name": "Python"})
    response = client.get("/courses")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_course(client):
    created = client.post("/courses", json={"name": "Python"})
    course_id = created.json()["id"]

    response = client.put(
        f"/courses/{course_id}",
        json={"name": "Advanced Python"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Advanced Python"


def test_duplicate_course_enrollment(client):
    student = create_test_student(client).json()
    course = client.post(
        "/courses",
        json={"name": "Python"},
    ).json()

    url = f"/students/{student['id']}/courses/{course['id']}"

    first = client.post(url)
    second = client.post(url)

    assert first.status_code == 200
    assert second.status_code == 409


def test_get_student_courses(client):
    student = create_test_student(client).json()
    course = client.post(
        "/courses",
        json={"name": "Python"},
    ).json()

    client.post(
        f"/students/{student['id']}/courses/{course['id']}"
    )

    response = client.get(
        f"/students/{student['id']}/courses"
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Python"


def test_disconnect_student_course(client):
    student = create_test_student(client).json()
    course = client.post(
        "/courses",
        json={"name": "Python"},
    ).json()

    url = f"/students/{student['id']}/courses/{course['id']}"
    client.post(url)

    response = client.delete(url)

    assert response.status_code == 200


def test_delete_course(client):
    course = client.post(
        "/courses",
        json={"name": "Python"},
    ).json()

    response = client.delete(f"/courses/{course['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Course deleted successfully"
