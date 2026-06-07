from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from app.core.exceptions import BadRequestException, ConflictException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.output_type import OutputType
from app.services.logs.audit_service import audit_service


class OutputTypeService:
    async def list_output_types(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[OutputType], int]:
        offset = (page - 1) * page_size
        total = (await db.execute(select(func.count()).select_from(OutputType))).scalar_one()
        result = await db.execute(
            select(OutputType).order_by(OutputType.type_name.asc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_output_type(self, db: AsyncSession, *, output_type_id: UUID) -> OutputType | None:
        result = await db.execute(select(OutputType).where(OutputType.output_type_id == output_type_id))
        return result.scalar_one_or_none()

    async def get_output_type_by_code(self, db: AsyncSession, *, type_code: str) -> OutputType | None:
        result = await db.execute(select(OutputType).where(OutputType.type_code == type_code))
        return result.scalar_one_or_none()

    async def create_output_type(
        self,
        db: AsyncSession,
        *,
        type_code: str,
        type_name: str,
        description: str | None,
        is_active: bool,
        actor_user_id: UUID, # ai tạo record này 
    ) -> OutputType:
        if await self.get_output_type_by_code(db, type_code=type_code):
            raise ConflictException("type_code đã tồn tại")

        output_type = OutputType(
            type_code=type_code,
            type_name=type_name,
            description=description,
            is_active=is_active,
        )
        db.add(output_type)
        await db.flush()
        await db.refresh(output_type)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="CREATE_OUTPUT_TYPE",
            target_schema="reference",
            target_table="output_types",
            target_id=output_type.output_type_id,
            new_value={
                "type_code": output_type.type_code,
                "type_name": output_type.type_name,
                "description": output_type.description,
                "is_active": output_type.is_active,
            },
            message="Created output type",
        )

        return output_type

    async def update_output_type(
        self,
        db: AsyncSession,
        *,
        output_type_id: UUID,
        actor_user_id: UUID,
        type_code: str | None,
        type_name: str | None,
        description: str | None,
        is_active: bool | None,
        fields_set: set[str],
    ) -> OutputType | None:
        output_type = await self.get_output_type(db, output_type_id=output_type_id)
        if output_type is None:
            return None

        old_value = {
            "type_code": output_type.type_code,
            "type_name": output_type.type_name,
            "description": output_type.description,
            "is_active": output_type.is_active,
        }

        if "type_code" in fields_set:
            if type_code is None:
                raise BadRequestException("type_code không được để trống")
            existing = await self.get_output_type_by_code(db, type_code=type_code)
            if existing and existing.output_type_id != output_type_id:
                raise ConflictException("type_code đã tồn tại")
            output_type.type_code = type_code

        if "type_name" in fields_set:
            if type_name is None:
                raise BadRequestException("type_name không được để trống")
            output_type.type_name = type_name

        if "description" in fields_set:
            output_type.description = description

        if "is_active" in fields_set:
            output_type.is_active = bool(is_active)

        output_type.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(output_type)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="UPDATE_OUTPUT_TYPE",
            target_schema="reference",
            target_table="output_types",
            target_id=output_type.output_type_id,
            old_value=old_value,
            new_value={
                "type_code": output_type.type_code,
                "type_name": output_type.type_name,
                "description": output_type.description,
                "is_active": output_type.is_active,
            },
            message="Updated output type",
        )

        return output_type

    async def delete_output_type(
        self,
        db: AsyncSession,
        *,
        output_type_id: UUID,
        actor_user_id: UUID,
    ) -> bool:
        output_type = await self.get_output_type(db, output_type_id=output_type_id)
        if output_type is None:
            return False

        old_value = {
            "type_code": output_type.type_code,
            "type_name": output_type.type_name,
            "description": output_type.description,
            "is_active": output_type.is_active,
        }

        await db.delete(output_type)
        await db.flush()

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="DELETE_OUTPUT_TYPE",
            target_schema="reference",
            target_table="output_types",
            target_id=output_type_id,
            old_value=old_value,
            message="Deleted output type",
        )

        return True


output_type_service = OutputTypeService()
