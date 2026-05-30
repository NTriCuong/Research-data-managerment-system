
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.auth import AdminResetPasswordRequest, ChangePasswordRequest, LoginRequest, MessageResponse, TokenResponse
from app.schemas.auth import LoginRequest, MessageResponse, TokenResponse, UserTokenOut
from app.schemas.user import UserRead
from app.services.auth.auth_service import auth_service
from app.services.auth.deps import get_current_active_user, get_valid_refresh_token

router = APIRouter()


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


def _user_token_out(user: User) -> UserTokenOut:
    return UserTokenOut(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.role_name,
        department_name=user.department.department_name if user.department else None,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    access_token, refresh_token, user = await auth_service.login(
        db,
        username=payload.username,
        password=payload.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE * 24 * 60 * 60,
    )
    await _commit_if_supported(db)

    return TokenResponse(access_token=access_token, user=_user_token_out(user))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    token_and_user: tuple = Depends(get_valid_refresh_token),
) -> TokenResponse:
    db_token, user = token_and_user
    access_token, new_refresh_token = await auth_service.refresh_token(
        db,
        db_token=db_token,
        user=user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE * 24 * 60 * 60,
    )
    await _commit_if_supported(db)

    return TokenResponse(access_token=access_token, user=_user_token_out(user))


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    token_and_user: tuple = Depends(get_valid_refresh_token),
) -> MessageResponse:
    db_token, _ = token_and_user
    await auth_service.logout(db, db_token=db_token)
    await _commit_if_supported(db)
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Logged out")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await auth_service.change_password(
        db,
        user=current_user,
        old_password=payload.current_password,
        new_password=payload.new_password,
    )
    await _commit_if_supported(db)
    return MessageResponse(message="Password changed successfully")


@router.post("/admin/reset-password/{user_id}", response_model=MessageResponse)
async def admin_reset_password(
    user_id: UUID,
    payload: AdminResetPasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    if current_user.role.role_code != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await auth_service.admin_reset_password(
        db,
        actor=current_user,
        user_id=user_id,
        new_password=payload.new_password,
    )
    await _commit_if_supported(db)
    return MessageResponse(message="Password reset successfully")