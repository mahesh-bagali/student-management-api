from pydantic import BaseModel, model_validator


class StudentCreate(BaseModel):
    name: str
    age: int
    profile_photo: str | None = None

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str