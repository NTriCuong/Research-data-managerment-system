from collections.abc import Iterable

from fastapi import Depends, HTTPException, status

from app.models.auth.user import User
from app.services.auth.deps import get_current_active_user


async def get_current_user(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user


def require_roles(*role_codes: str):
    allowed = set(role_codes)

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_code = current_user.role.role_code if current_user.role else None
        if user_role_code not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return dependency


def has_role(user: User, role_codes: Iterable[str]) -> bool:
    user_role_code = user.role.role_code if user.role else None
    return user_role_code in set(role_codes)
