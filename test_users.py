
import pytest

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

    test_client = TestClient(app)
    yield test_client

    test_client.close()
    app.dependency_overrides.clear()
    test_engine.dispose()


def register_user(client):
    return client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Test12345",
            "confirm_password": "Test12345",
        },
    )


def login_user(client):
    return client.post(
        "/login",
        data={
            "username": "test@example.com",
            "password": "Test12345",
        },
    )


def test_register(client):
    response = register_user(client)

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "password_hash" not in response.json()


def test_login(client):
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_profile(client):
    register_user(client)
    login_response = login_user(client)

    token = login_response.json()["access_token"]

    response = client.get(
        "/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_refresh_token(client):
    register_user(client)
    login_response = login_user(client)

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/refresh",
        params={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_admin_forbidden(client):
    register_user(client)
    login_response = login_user(client)

    token = login_response.json()["access_token"]

    response = client.get(
        "/admin",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
