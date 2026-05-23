from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    email: EmailStr
    full_name: str
    role_id: UUID
    department_id: UUID | None = None
    status: str
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
