from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(LoginRequest):
    password_confirm: str = Field(..., min_length=6)

    # Add validation
    def model_post_init(self, __context) -> None:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: float  # expiration time
