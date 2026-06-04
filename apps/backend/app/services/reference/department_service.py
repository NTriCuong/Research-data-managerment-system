from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.department import Department
from app.services.logs.audit_service import audit_service


class DepartmentService:
    async def list_departments(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Department], int]:
        offset = (page - 1) * page_size
        total = (await db.execute(select(func.count()).select_from(Department))).scalar_one()
        result = await db.execute(
            select(Department).order_by(Department.department_name.asc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_department(self, db: AsyncSession, *, department_id: UUID) -> Department | None:
        result = await db.execute(select(Department).where(Department.department_id == department_id))
        return result.scalar_one_or_none()

    async def get_department_by_code(self, db: AsyncSession, *, department_code: str) -> Department | None:
        result = await db.execute(select(Department).where(Department.department_code == department_code))
        return result.scalar_one_or_none()

    async def create_department(
        self,
        db: AsyncSession,
        *,
        department_code: str,
        department_name: str,
        actor_user_id: UUID,
        parent_department_id: UUID | None,
        description: str | None,
        is_active: bool,
        ip_address: str | None,
        user_agent: str | None,
    ) -> Department:
        if parent_department_id is not None:
            parent = await self.get_department(db, department_id=parent_department_id)
            if parent is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent department not found")

        department = Department(
            department_code=department_code,
            department_name=department_name,
            parent_department_id=parent_department_id,
            description=description,
            is_active=is_active,
        )
        db.add(department)
        await db.flush()
        await db.refresh(department)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="CREATE_DEPARTMENT",
            target_schema="reference",
            target_table="departments",
            target_id=department.department_id,
            new_value={
                "department_code": department.department_code,
                "department_name": department.department_name,
                "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
                "description": department.description,
                "is_active": department.is_active,
            },
            message="Created department",
        )

        return department

    async def update_department(
        self,
        db: AsyncSession,
        *,
        department_id: UUID,
        actor_user_id: UUID,
        department_code: str | None,
        department_name: str | None,
        parent_department_id: UUID | None,
        description: str | None,
        is_active: bool | None,
        ip_address: str | None,
        user_agent: str | None,
        fields_set: set[str],
    ) -> Department | None:
        department = await self.get_department(db, department_id=department_id)
        if department is None:
            return None

        old_value = {
            "department_code": department.department_code,
            "department_name": department.department_name,
            "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
            "description": department.description,
            "is_active": department.is_active,
        }

        if "parent_department_id" in fields_set:
            if parent_department_id == department_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department cannot be its own parent")
            if parent_department_id is not None:
                parent = await self.get_department(db, department_id=parent_department_id)
                if parent is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent department not found")
            department.parent_department_id = parent_department_id

        if "department_code" in fields_set:
            if department_code is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="department_code cannot be null")
            department.department_code = department_code
        if "department_name" in fields_set:
            if department_name is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="department_name cannot be null")
            department.department_name = department_name
        if "description" in fields_set:
            department.description = description
        if "is_active" in fields_set:
            department.is_active = bool(is_active)

        department.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(department)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="UPDATE_DEPARTMENT",
            target_schema="reference",
            target_table="departments",
            target_id=department.department_id,
            old_value=old_value,
            new_value={
                "department_code": department.department_code,
                "department_name": department.department_name,
                "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
                "description": department.description,
                "is_active": department.is_active,
            },
            message="Updated department",
        )
        return department

    async def delete_department(
        self,
        db: AsyncSession,
        *,
        department_id: UUID,
        actor_user_id: UUID,
        ip_address: str | None,
        user_agent: str | None,
    ) -> bool:
        department = await self.get_department(db, department_id=department_id)
        if department is None:
            return False

        old_value = {
            "department_code": department.department_code,
            "department_name": department.department_name,
            "parent_department_id": str(department.parent_department_id) if department.parent_department_id else None,
            "description": department.description,
            "is_active": department.is_active,
        }

        await db.delete(department)
        await db.flush()

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="DELETE_DEPARTMENT",
            target_schema="reference",
            target_table="departments",
            target_id=department_id,
            old_value=old_value,
            message="Deleted department",
        )
        return True


department_service = DepartmentService()
