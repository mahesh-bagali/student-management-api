
import jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from config import SECRET_KEY, ALGORITHM
from database import User, get_session
from sqlmodel import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Get current authenticated user
def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if (
            user_id is None
            or not user_id.isdigit()
            or token_type != "access"
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Admin authorization
def require_admin(
    user_id: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = session.get(User, int(user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return user


# Verify refresh token
def get_user_id_from_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if (
            user_id is None
            or not user_id.isdigit()
            or token_type != "refresh"
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token",
            )

        return user_id

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )
