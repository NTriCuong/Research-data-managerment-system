from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class UserTokenOut(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    full_name: str
    role_name: str
    department_name: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserTokenOut


class MessageResponse(BaseModel):
    message: str
