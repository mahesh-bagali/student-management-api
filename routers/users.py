
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from dependencies.auth import (
    get_current_user,
    require_admin,
    get_user_id_from_refresh_token,
)

from database import User, get_session
from schemas import UserCreate, UserResponse

from security import (
    create_access_token,
    create_refresh_token,
    password_hash,
)

from rate_limiter import limiter


router = APIRouter(
    tags=["Users"]
)


# Register
@router.post(
    "/register",
    response_model=UserResponse,
    summary="Register user",
    description="Create a new user account with name, email and password."
)
def register(
    user: UserCreate,
    session: Session = Depends(get_session),
):
    hashed_password = password_hash.hash(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


# Login
@router.post(
    "/login",
    summary="Login user",
    description="Authenticate a user and generate access and refresh tokens."
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    statement = select(User).where(
        User.email == form_data.username
    )

    db_user = session.exec(statement).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not password_hash.verify(
        form_data.password,
        db_user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(db_user.id)
    refresh_token = create_refresh_token(db_user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Refresh access token
@router.post(
    "/refresh",
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token."
)
def refresh_access_token(
    refresh_token: str,
):
    user_id = get_user_id_from_refresh_token(refresh_token)

    new_access_token = create_access_token(int(user_id))

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


# User profile
@router.get(
    "/profile",
    summary="Get user profile",
    description="Retrieve the profile of the currently authenticated user."
)
def profile(
    user_id: str = Depends(get_current_user),
):
    return {
        "message": "Welcome to your profile",
        "user_id": user_id,
    }


# Admin dashboard
@router.get(
    "/admin",
    summary="Admin dashboard",
    description="Access the admin dashboard. Requires administrator privileges."
)
def admin_dashboard(
    user: User = Depends(require_admin),
):
    return {
        "message": "Welcome to admin dashboard",
        "user": user.name,
        "role": user.role,
    }
