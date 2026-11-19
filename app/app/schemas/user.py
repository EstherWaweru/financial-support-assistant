from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: str
    hashed_password: str


class UserUpdate(BaseModel):
    pass


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserRegisterResponse(BaseModel):
    email: str
    id: UUID
