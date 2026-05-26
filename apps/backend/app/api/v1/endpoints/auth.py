from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.database.config import get_db
from app.models.auth.user import User
from app.schemas.auth import LoginRequest, MessageResponse, TokenResponse
from app.schemas.user import UserRead
from app.services.auth.auth_service import auth_service
from app.services.auth.deps import get_current_active_user, get_valid_refresh_token
from app.services.auth.security import decode_access_token

router = APIRouter()


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    access_token, refresh_token = await auth_service.login(
        db,
        email=payload.email,
        password=payload.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    payload_data = decode_access_token(access_token)
    user_id = payload_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token missing subject")

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.user_id == UUID(str(user_id)))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authenticated user not found")

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE * 24 * 60 * 60,
    )
    await _commit_if_supported(db)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


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

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))


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


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_active_user)) -> UserRead:
    return UserRead.model_validate(current_user)
