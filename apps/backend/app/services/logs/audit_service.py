from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs.audit_log import AuditLog


class AuditService:
    async def write_log(
        self,
        db: AsyncSession,
        *,
        actor_user_id: UUID | None,
        action_code: str,
        target_schema: str | None = None,
        target_table: str | None = None,
        target_id: UUID | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        result: str = "success",
        message: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        db.add(
            AuditLog(
                actor_user_id=actor_user_id,
                action_code=action_code,
                target_schema=target_schema,
                target_table=target_table,
                target_id=target_id,
                old_value=old_value,
                new_value=new_value,
                result=result,
                message=message,
                created_at=created_at or datetime.now(),
            )
        )
        await db.flush()


audit_service = AuditService()
