from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.reference import DepartmentCreate, DepartmentOut, DepartmentUpdate
from app.services.reference.department_service import department_service

router = APIRouter()

ALLOWED_REFERENCE_READ_ROLES = ("SUPER_ADMIN", "REVIEWER", "DATA_ENTRY")


async def _commit_if_supported(db: AsyncSession) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await commit()


@router.get("", response_model=list[DepartmentOut])
async def list_departments(
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[DepartmentOut]:
    departments = await department_service.list_departments(db)
    return [DepartmentOut.model_validate(d) for d in departments]


@router.get("/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    department = await department_service.get_department(db, department_id=department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return DepartmentOut.model_validate(department)


@router.post("", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    existing = await department_service.get_department_by_code(db, department_code=payload.department_code)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Department code '{payload.department_code}' already exists",
        )

    department = await department_service.create_department(
        db,
        department_code=payload.department_code,
        department_name=payload.department_name,
        actor_user_id=current_user.user_id,
        parent_department_id=payload.parent_department_id,
        description=payload.description,
        is_active=payload.is_active,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    await _commit_if_supported(db)
    return DepartmentOut.model_validate(department)


@router.put("/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    if payload.department_code is not None:
        existing = await department_service.get_department_by_code(db, department_code=payload.department_code)
        if existing is not None and existing.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Department code '{payload.department_code}' already exists",
            )

    department = await department_service.update_department(
        db,
        department_id=department_id,
        actor_user_id=current_user.user_id,
        department_code=payload.department_code,
        department_name=payload.department_name,
        parent_department_id=payload.parent_department_id,
        description=payload.description,
        is_active=payload.is_active,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        fields_set=payload.model_fields_set,
    )
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    await _commit_if_supported(db)
    return DepartmentOut.model_validate(department)


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await department_service.delete_department(
        db,
        department_id=department_id,
        actor_user_id=current_user.user_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    await _commit_if_supported(db)
