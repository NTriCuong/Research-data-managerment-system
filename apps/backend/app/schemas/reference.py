from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    department_code: str
    department_name: str
    parent_department_id: UUID | None = None
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    department_code: str | None = None
    department_name: str | None = None
    parent_department_id: UUID | None = None
    description: str | None = None
    is_active: bool | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: UUID
    department_code: str
    department_name: str
    parent_department_id: UUID | None
    description: str | None
    is_active: bool