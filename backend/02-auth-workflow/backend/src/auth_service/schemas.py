from pydantic import BaseModel, EmailStr, Field


class RegisterBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=2, max_length=80)


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyBody(BaseModel):
    token: str = Field(min_length=16, max_length=200)


class ResendBody(BaseModel):
    email: EmailStr


class Profile(BaseModel):
    id: int
    email: str
    name: str
    email_verified: bool = True
