from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.core.exceptions import NotFoundException
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.reference import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    KeywordCreate,
    KeywordOut,
    KeywordUpdate,
    OutputTypeCreate,
    OutputTypeOut,
    OutputTypeUpdate,
    PaginatedResponse,
    ResearchDomainCreate,
    ResearchDomainOut,
    ResearchDomainUpdate,
    ResearcherCreate,
    ResearcherOut,
    ResearcherUpdate,
)
from app.services.reference.department_service import department_service
from app.services.reference.keyword_service import keyword_service
from app.services.reference.output_types_service import output_type_service
from app.services.reference.research_domain_service import research_domain_service
from app.services.reference.researcher_service import researcher_service

router = APIRouter()

ALLOWED_REFERENCE_READ_ROLES = ("SUPER_ADMIN", "REVIEWER", "DATA_ENTRY", "APPROVER")
ALLOWED_REFERENCE_CREATE_ROLES = ("SUPER_ADMIN", "DATA_ENTRY")


@router.get("/departments", response_model=PaginatedResponse[DepartmentOut])
async def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DepartmentOut]:
    items, total = await department_service.list_departments(db, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[DepartmentOut.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size),
    )


@router.get("/department/{department_id}", response_model=DepartmentOut)
async def get_department(
    department_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
    department = await department_service.get_department(db, department_id=department_id)
    if department is None:
        raise NotFoundException("Không tìm thấy đơn vị")
    return DepartmentOut.model_validate(department)


@router.post("/department", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
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
    return DepartmentOut.model_validate(department)


@router.put("/department/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: UUID,
    payload: DepartmentUpdate,
    request: Request,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> DepartmentOut:
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
        raise NotFoundException("Không tìm thấy đơn vị")

    return DepartmentOut.model_validate(department)


@router.delete("/department/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
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
        raise NotFoundException("Không tìm thấy đơn vị")

# ── OutputType ────────────────────────────────────────────────────────────────

@router.get("/output-types/", response_model=PaginatedResponse[OutputTypeOut])
async def list_output_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OutputTypeOut]:
    items, total = await output_type_service.list_output_types(db, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[OutputTypeOut.model_validate(o) for o in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size),
    )


@router.get("/output-types/{output_type_id}", response_model=OutputTypeOut)
async def get_output_type(
    output_type_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> OutputTypeOut:
    output_type = await output_type_service.get_output_type(db, output_type_id=output_type_id)
    if output_type is None:
        raise NotFoundException("Không tìm thấy loại sản phẩm")
    return OutputTypeOut.model_validate(output_type)


@router.post("/output-types/", response_model=OutputTypeOut, status_code=status.HTTP_201_CREATED)
async def create_output_type(
    payload: OutputTypeCreate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> OutputTypeOut:
    output_type = await output_type_service.create_output_type(
        db,
        type_code=payload.type_code,
        type_name=payload.type_name,
        description=payload.description,
        is_active=payload.is_active,
        actor_user_id=current_user.user_id,
    )
    return OutputTypeOut.model_validate(output_type)


@router.put("/output-types/{output_type_id}", response_model=OutputTypeOut)
async def update_output_type(
    output_type_id: UUID,
    payload: OutputTypeUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> OutputTypeOut:
    output_type = await output_type_service.update_output_type(
        db,
        output_type_id=output_type_id,
        actor_user_id=current_user.user_id,
        type_code=payload.type_code,
        type_name=payload.type_name,
        description=payload.description,
        is_active=payload.is_active,
        fields_set=payload.model_fields_set,
    )
    if output_type is None:
        raise NotFoundException("Không tìm thấy loại sản phẩm")
    return OutputTypeOut.model_validate(output_type)


@router.delete("/output-types/{output_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_type(
    output_type_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await output_type_service.delete_output_type(
        db,
        output_type_id=output_type_id,
        actor_user_id=current_user.user_id,
    )
    if not deleted:
        raise NotFoundException("Không tìm thấy loại sản phẩm")
# ── ResearchDomain ────────────────────────────────────────────────────────────

@router.get("/research-domains/", response_model=PaginatedResponse[ResearchDomainOut])
async def list_research_domains(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ResearchDomainOut]:
    items, total = await research_domain_service.list_research_domains(db, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[ResearchDomainOut.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size),
    )


@router.get("/research-domains/suggestions", response_model=list[ResearchDomainOut])
async def suggest_research_domains(
    q: str | None = Query(default=None, max_length=255),
    limit: int = Query(default=10, ge=1, le=50),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[ResearchDomainOut]:
    domains = await research_domain_service.suggest_research_domains(db, q=q, limit=limit)
    return [ResearchDomainOut.model_validate(domain) for domain in domains]


@router.get("/research-domains/{domain_id}", response_model=ResearchDomainOut)
async def get_research_domain(
    domain_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> ResearchDomainOut:
    domain = await research_domain_service.get_research_domain(db, domain_id=domain_id)
    if domain is None:
        raise NotFoundException("Không tìm thấy lĩnh vực nghiên cứu")
    return ResearchDomainOut.model_validate(domain)


@router.post("/research-domains/", response_model=ResearchDomainOut, status_code=status.HTTP_201_CREATED)
async def create_research_domain(
    payload: ResearchDomainCreate,
    current_user: User = Depends(require_roles(*ALLOWED_REFERENCE_CREATE_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> ResearchDomainOut:
    domain = await research_domain_service.create_research_domain(
        db,
        domain_code=payload.domain_code,
        domain_name=payload.domain_name,
        parent_domain_id=payload.parent_domain_id,
        description=payload.description,
        is_active=payload.is_active,
        actor_user_id=current_user.user_id,
    )
    return ResearchDomainOut.model_validate(domain)


@router.put("/research-domains/{domain_id}", response_model=ResearchDomainOut)
async def update_research_domain(
    domain_id: UUID,
    payload: ResearchDomainUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> ResearchDomainOut:
    domain = await research_domain_service.update_research_domain(
        db,
        domain_id=domain_id,
        actor_user_id=current_user.user_id,
        domain_code=payload.domain_code,
        domain_name=payload.domain_name,
        parent_domain_id=payload.parent_domain_id,
        description=payload.description,
        is_active=payload.is_active,
        fields_set=payload.model_fields_set,
    )
    if domain is None:
        raise NotFoundException("Không tìm thấy lĩnh vực nghiên cứu")
    return ResearchDomainOut.model_validate(domain)


@router.delete("/research-domains/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_domain(
    domain_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await research_domain_service.delete_research_domain(
        db,
        domain_id=domain_id,
        actor_user_id=current_user.user_id,
    )
    if not deleted:
        raise NotFoundException("Không tìm thấy lĩnh vực nghiên cứu")
# ── Researcher ────────────────────────────────────────────────────────────────

@router.get("/researchers/", response_model=PaginatedResponse[ResearcherOut])
async def list_researchers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ResearcherOut]:
    items, total = await researcher_service.list_researchers(db, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[ResearcherOut.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size),
    )


@router.get("/researchers/suggestions", response_model=list[ResearcherOut])
async def suggest_researchers(
    q: str | None = Query(default=None, max_length=255),
    limit: int = Query(default=10, ge=1, le=50),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[ResearcherOut]:
    researchers = await researcher_service.suggest_researchers(db, q=q, limit=limit)
    return [ResearcherOut.model_validate(researcher) for researcher in researchers]


@router.get("/researchers/{researcher_id}", response_model=ResearcherOut)
async def get_researcher(
    researcher_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> ResearcherOut:
    researcher = await researcher_service.get_researcher(db, researcher_id=researcher_id)
    if researcher is None:
        raise NotFoundException("Không tìm thấy nhà nghiên cứu")
    return ResearcherOut.model_validate(researcher)


@router.post("/researchers/", response_model=ResearcherOut, status_code=status.HTTP_201_CREATED)
async def create_researcher(
    payload: ResearcherCreate,
    current_user: User = Depends(require_roles(*ALLOWED_REFERENCE_CREATE_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> ResearcherOut:
    researcher = await researcher_service.create_researcher(
        db,
        full_name=payload.full_name,
        email=payload.email,
        orcid=payload.orcid,
        department_id=payload.department_id,
        academic_title=payload.academic_title,
        researcher_code=payload.researcher_code,
        is_internal=payload.is_internal,
        actor_user_id=current_user.user_id,
    )
    return ResearcherOut.model_validate(researcher)


@router.put("/researchers/{researcher_id}", response_model=ResearcherOut)
async def update_researcher(
    researcher_id: UUID,
    payload: ResearcherUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> ResearcherOut:
    researcher = await researcher_service.update_researcher(
        db,
        researcher_id=researcher_id,
        actor_user_id=current_user.user_id,
        full_name=payload.full_name,
        email=payload.email,
        orcid=payload.orcid,
        department_id=payload.department_id,
        academic_title=payload.academic_title,
        researcher_code=payload.researcher_code,
        is_internal=payload.is_internal,
        fields_set=payload.model_fields_set,
    )
    if researcher is None:
        raise NotFoundException("Không tìm thấy nhà nghiên cứu")
    return ResearcherOut.model_validate(researcher)


@router.delete("/researchers/{researcher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_researcher(
    researcher_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await researcher_service.delete_researcher(
        db,
        researcher_id=researcher_id,
        actor_user_id=current_user.user_id,
    )
    if not deleted:
        raise NotFoundException("Không tìm thấy nhà nghiên cứu")
# ── Keyword ───────────────────────────────────────────────────────────────────

@router.get("/keywords/", response_model=PaginatedResponse[KeywordOut])
async def list_keywords(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[KeywordOut]:
    items, total = await keyword_service.list_keywords(db, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[KeywordOut.model_validate(k) for k in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=-(-total // page_size),
    )


@router.get("/keywords/suggestions", response_model=list[KeywordOut])
async def suggest_keywords(
    q: str | None = Query(default=None, max_length=255),
    limit: int = Query(default=10, ge=1, le=50),
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> list[KeywordOut]:
    keywords = await keyword_service.suggest_keywords(db, q=q, limit=limit)
    return [KeywordOut.model_validate(keyword) for keyword in keywords]


@router.get("/keywords/{keyword_id}", response_model=KeywordOut)
async def get_keyword(
    keyword_id: UUID,
    _: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> KeywordOut:
    keyword = await keyword_service.get_keyword(db, keyword_id=keyword_id)
    if keyword is None:
        raise NotFoundException("Không tìm thấy từ khóa")
    return KeywordOut.model_validate(keyword)


@router.post("/keywords/", response_model=KeywordOut, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    payload: KeywordCreate,
    current_user: User = Depends(require_roles(*ALLOWED_REFERENCE_READ_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> KeywordOut:
    keyword = await keyword_service.create_keyword(
        db,
        keyword_text=payload.keyword_text,
        normalized_text=payload.normalized_text,
        actor_user_id=current_user.user_id,
    )
    return KeywordOut.model_validate(keyword)


@router.put("/keywords/{keyword_id}", response_model=KeywordOut)
async def update_keyword(
    keyword_id: UUID,
    payload: KeywordUpdate,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> KeywordOut:
    keyword = await keyword_service.update_keyword(
        db,
        keyword_id=keyword_id,
        actor_user_id=current_user.user_id,
        keyword_text=payload.keyword_text,
        normalized_text=payload.normalized_text,
        fields_set=payload.model_fields_set,
    )
    if keyword is None:
        raise NotFoundException("Không tìm thấy từ khóa")
    return KeywordOut.model_validate(keyword)


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: UUID,
    current_user: User = Depends(require_roles("SUPER_ADMIN")),
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await keyword_service.delete_keyword(
        db,
        keyword_id=keyword_id,
        actor_user_id=current_user.user_id,
    )
    if not deleted:
        raise NotFoundException("Không tìm thấy từ khóa")
