from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.enum import UserStatus
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import MessageResponse
from app.schemas.user import UserCreate, UserRead, UserRoleUpdate, UserStatusUpdate, UserUpdate
from app.services.auth.auth_service import auth_service

router = APIRouter()


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(require_roles("SUPER_ADMIN", "DATA_ENTRY", "REVIEWER", "APPROVER", "MANAGER", "PUBLIC_USER"))) -> UserRead:
    return UserRead.model_validate(current_user)


@router.get("", response_model=list[UserRead])
async def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, max_length=150),
    role_id: UUID | None = Query(default=None),
    status_filter: UserStatus | None = Query(default=None, alias="status"),
    _: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    repo = AuthRepository(db)
    users = await repo.list_users(
        limit=limit,
        offset=offset,
        q=q,
        role_id=role_id,
        status=status_filter.value if status_filter else None,
    )
    return [UserRead.model_validate(user) for user in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: UUID,
    _: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.user_id == user_id)
        .where(User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    role = await db.scalar(select(Role).where(Role.role_id == payload.role_id))
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

    user = await auth_service.create_user(
        db,
        actor=current_user,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role_id=payload.role_id,
        department_id=payload.department_id,
    )
    await _commit_if_supported(db)
    return UserRead.model_validate(user)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await auth_service.update_user(
        db,
        actor=current_user,
        user_id=user_id,
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        department_id=payload.department_id,
        fields_set=payload.model_fields_set,
    )
    await _commit_if_supported(db)
    return UserRead.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def soft_delete_user(
    user_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    await auth_service.soft_delete_user(db, actor=current_user, user_id=user_id)
    await _commit_if_supported(db)
    return MessageResponse(message="User soft-deleted")


@router.put("/{user_id}/status", response_model=UserRead)
async def update_user_status(
    user_id: UUID,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await auth_service.update_user_status(
        db,
        actor=current_user,
        user_id=user_id,
        new_status=payload.status,
    )
    await _commit_if_supported(db)
    return UserRead.model_validate(user)


@router.put("/{user_id}/role", response_model=UserRead)
async def assign_role(
    user_id: UUID,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    role = await db.scalar(select(Role).where(Role.role_id == payload.role_id))
    if role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found")

    user = await auth_service.update_user_role(
        db,
        actor=current_user,
        user_id=user_id,
        role_id=payload.role_id,
    )
    await _commit_if_supported(db)
    await db.refresh(user)
    return UserRead.model_validate(user)

