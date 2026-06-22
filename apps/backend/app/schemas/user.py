from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enum import UserStatus


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    email: EmailStr
    full_name: str
    role_id: UUID
    department_id: UUID | None = None
    status: UserStatus
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role_id: UUID
    department_id: UUID | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    department_id: UUID | None = None


class UserRoleUpdate(BaseModel):
    role_id: UUID


class UserStatusUpdate(BaseModel):
    status: UserStatus


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: UUID
    role_code: str
    role_name: str

