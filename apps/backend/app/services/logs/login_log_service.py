
import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.logs.login_log import LoginLog


logger = logging.getLogger(__name__)

class LoginLogService:
    async def write_log(
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

login_log_service = LoginLogService()
   