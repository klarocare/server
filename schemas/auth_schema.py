from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from schemas.care_task_schema import Caregiver, CareTask


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(LoginRequest, Caregiver):
    """
    Combines login credentials with caregiver information for registration
    """
    password_confirm: str = Field(..., min_length=6)

    # Add validation
    def model_post_init(self, __context) -> None:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Caregiver


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: float  # expiration time


class UserResponse(Caregiver):
    """
    Public user information returned by the API
    """
    email: EmailStr 