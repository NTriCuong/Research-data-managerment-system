import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.department import Department
from app.services.logs.logs_service import LogService


class DepartmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.log_svc = LogService(db)  # cùng session → cùng transaction

    async def create_department(
        self,
        department_code: str,
        department_name: str,
        actor_user_id: uuid.UUID | None = None,
        parent_department_id: uuid.UUID | None = None,
        description: str | None = None,
        is_active: bool = True,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Department:
        department = Department(
            department_code=department_code,
            department_name=department_name,
            parent_department_id=parent_department_id,
            description=description,
            is_active=is_active,
        )

        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)

        await self.log_svc.write_audit_log(
            action_code="CREATE",
            actor_user_id=actor_user_id,
            target_schema="public",
            target_table="departments",
            target_id=department.department_id,
            new_value={
                "department_code": department_code,
                "department_name": department_name,
                "parent_department_id": str(parent_department_id) if parent_department_id else None,
                "description": description,
                "is_active": is_active,
            },
            result="success",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

        return department

    async def get_department(
        self,
        department_id: uuid.UUID,
    ) -> Department | None:
        result = await self.db.execute(
            select(Department).where(
                Department.department_id == department_id
            )
        )

        return result.scalar_one_or_none()

    async def get_department_by_code(
        self,
        department_code: str,
    ) -> Department | None:
        result = await self.db.execute(
            select(Department).where(
                Department.department_code == department_code
            )
        )

        return result.scalar_one_or_none()

    async def update_department(
        self,
        department_id: uuid.UUID,
        actor_user_id: uuid.UUID | None = None,
        department_code: str | None = None,
        department_name: str | None = None,
        parent_department_id: uuid.UUID | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Department | None:
        department = await self.get_department(department_id)

        if not department:
            return None

        # snapshot trước khi thay đổi để ghi vào old_value
        old_value = {
            "department_code": department.department_code,
            "department_name": department.department_name,
            "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
            "description": department.description,
            "is_active": department.is_active,
        }

        if department_code is not None:
            department.department_code = department_code

        if department_name is not None:
            department.department_name = department_name

        if parent_department_id is not None:
            department.parent_department_id = parent_department_id

        if description is not None:
            department.description = description

        if is_active is not None:
            department.is_active = is_active

        await self.db.commit()
        await self.db.refresh(department)

        await self.log_svc.write_audit_log(
            action_code="UPDATE",
            actor_user_id=actor_user_id,
            target_schema="public",
            target_table="departments",
            target_id=department_id,
            old_value=old_value,
            new_value={
                "department_code": department.department_code,
                "department_name": department.department_name,
                "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
                "description": department.description,
                "is_active": department.is_active,
            },
            result="success",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

        return department

    async def delete_department(
        self,
        department_id: uuid.UUID,
        actor_user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> bool:
        department = await self.get_department(department_id)

        if not department:
            return False

        old_value = {
            "department_code": department.department_code,
            "department_name": department.department_name,
            "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
            "description": department.description,
            "is_active": department.is_active,
        }

        await self.db.delete(department)
        await self.db.commit()

        await self.log_svc.write_audit_log(
            action_code="DELETE",
            actor_user_id=actor_user_id,
            target_schema="public",
            target_table="departments",
            target_id=department_id,
            old_value=old_value,
            result="success",
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.db.commit()

        return True

    async def list_departments(self) -> list[Department]:
        result = await self.db.execute(
            select(Department)
        )

        return list(result.scalars().all())