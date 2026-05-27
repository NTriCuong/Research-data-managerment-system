from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.config import get_db
from app.models.auth.user import User
from app.schemas.department.request import DepartmentCreate, DepartmentUpdate
from app.schemas.department.response import DepartmentOut
from app.services.reference.department_service import DepartmentService

router = APIRouter()


# ── list all — tất cả role ────────────────────────────────────────────────────

@router.get("", response_model=list[DepartmentOut])
async def list_departments(
    current_user: User = Depends(require_roles("SUPER_ADMIN", "REVIEWER", "DATA_ENTRY")),
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentOut]:
    svc = DepartmentService(db)
    departments = await svc.list_departments()
    return [DepartmentOut.model_validate(d) for d in departments]


# ── get by id — tất cả role ───────────────────────────────────────────────────

@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN", "REVIEWER", "DATA_ENTRY")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    svc = DepartmentService(db)
    department = await svc.get_department(department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return DepartmentOut.model_validate(department)


# ── create — chỉ SUPER_ADMIN ──────────────────────────────────────────────────

@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    svc = DepartmentService(db)

    existing = await svc.get_department_by_code(payload.department_code)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department code '{payload.department_code}' already exists",
        )

    department = await svc.create_department(
        department_code=payload.department_code,
        department_name=payload.department_name,
        actor_user_id=current_user.user_id,
        parent_department_id=payload.parent_department_id,
        description=payload.description,
        is_active=payload.is_active,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return DepartmentOut.model_validate(department)


# ── update — chỉ SUPER_ADMIN ──────────────────────────────────────────────────

@router.put("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    svc = DepartmentService(db)

    if payload.department_code is not None:
        existing = await svc.get_department_by_code(payload.department_code)
        if existing is not None and existing.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Department code '{payload.department_code}' already exists",
            )

    department = await svc.update_department(
        department_id=department_id,
        actor_user_id=current_user.user_id,
        department_code=payload.department_code,
        department_name=payload.department_name,
        parent_department_id=payload.parent_department_id,
        description=payload.description,
        is_active=payload.is_active,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return DepartmentOut.model_validate(department)


# ── delete — chỉ SUPER_ADMIN ──────────────────────────────────────────────────

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    svc = DepartmentService(db)
    deleted = await svc.delete_department(
        department_id=department_id,
        actor_user_id=current_user.user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")