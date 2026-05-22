# app/api/deps.py
from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database.config import get_db
from app.crud import crud_user
from app.models.system.User import User

# Đọc access token từ Authorization: Bearer header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user( 
    request: Request,
    token: str = Depends(oauth2_scheme),   
    db: AsyncSession = Depends(get_db), 
) -> User:

    try:
        payload = decode_token(token) 
        if payload.get("type") != "access":
            raise HTTPException( 
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="token invalid", 
                    headers={"WWW-Authenticate": "Bearer"},
                )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="token invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await crud_user.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="token invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.current_user_id = user.id
    return user


async def get_current_active_user( 
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.is_deleted: 
        raise HTTPException(status_code=403, detail="Account has been deleted")

    if not current_user.is_active:  
        raise HTTPException(status_code=403, detail="Account is deactivated")

    if (
        current_user.locked_until is not None
        and current_user.locked_until > datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=403,
            detail=f"Account locked until {current_user.locked_until.isoformat()}",
        )

    return current_user


# RBAC 

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin":    {"*"},
    "researcher":       {"project:read", "dataset:read", "review:read"},
    "reviewer":       {"project:read", "project:approve", "dataset:read", "dataset:approve", "review:read"},
}


class RoleChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self,
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        role_name = current_user.role.name
        allowed   = ROLE_PERMISSIONS.get(role_name, set())

        if "*" in allowed:
            return current_user

        if self.required_permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' does not have permission '{self.required_permission}'",
            )
        return current_user


require_any_login       = Depends(get_current_active_user)
require_project_read    = Depends(RoleChecker("project:read"))
require_project_write   = Depends(RoleChecker("project:write"))
require_project_approve = Depends(RoleChecker("project:approve"))
require_dataset_read    = Depends(RoleChecker("dataset:read"))
require_dataset_write   = Depends(RoleChecker("dataset:write"))
require_user_read       = Depends(RoleChecker("user:read"))
require_user_write      = Depends(RoleChecker("user:write"))
require_user_delete     = Depends(RoleChecker("user:delete"))
require_audit_read      = Depends(RoleChecker("audit:read"))
require_review_write    = Depends(RoleChecker("review:write"))