
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enum import WorkflowStatus
from app.models.logs.audit_log import AuditLog
from app.models.logs.login_log import LoginLog
from app.models.logs.workflow_history import WorkflowHistory

logger = logging.getLogger(__name__)


class LogService:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # 1. AUDIT LOG — ghi lại thay đổi CRUD trên bất kỳ bảng nào

    async def write_audit_log(
        self,
        action_code: str,
        *,
        actor_user_id: UUID | None = None,
        target_schema: str | None = None,
        target_table: str | None = None,
        target_id: UUID | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        result: str = "success",
        message: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None, # mỗi lần browser hoặc app gửi HTTP request, nó tự động đính kèm header User-Agent mô tả bản thân
    ) -> None:
        try:
            self.session.add(
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
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
        except Exception: # ghi log thất bại
            raise HTTPException(status_code=500, detail="Internal Server Error") from None


    # 2. LOGIN LOG — ghi lại mọi lần đăng nhập (thành công / thất bại)

    async def write_login_log(
        self,
        login_result: str,
        *,
        user_id: UUID | None = None,
        username_attempted: str | None = None,
        failure_reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        
        try:
            self.session.add(
                LoginLog(
                    user_id=user_id,
                    username_attempted=username_attempted,
                    login_result=login_result,
                    failure_reason=failure_reason,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
        except Exception:
             raise HTTPException(status_code=500, detail="Internal Server Error") from None


   