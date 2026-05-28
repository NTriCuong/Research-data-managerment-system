from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    department_code: str
    department_name: str
    parent_department_id: UUID | None = None
    description: str | None = None
    is_active: bool = True


class DepartmentUpdate(BaseModel):
    department_code: str | None = None
    department_name: str | None = None
    parent_department_id: UUID | None = None
    description: str | None = None
    is_active: bool | None = None


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    department_id: UUID
    department_code: str
    department_name: str
    parent_department_id: UUID | None
    description: str | None
    is_active: bool


# ── OutputType ────────────────────────────────────────────────────────────────

class OutputTypeCreate(BaseModel):
    type_code: str
    type_name: str
    description: str | None = None
    is_active: bool = True


class OutputTypeUpdate(BaseModel):
    type_code: str | None = None
    type_name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class OutputTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    output_type_id: UUID
    type_code: str
    type_name: str
    description: str | None
    is_active: bool


# ── ResearchDomain ────────────────────────────────────────────────────────────

class ResearchDomainCreate(BaseModel):
    domain_code: str
    domain_name: str
    parent_domain_id: UUID | None = None
    description: str | None = None
    is_active: bool = True


class ResearchDomainUpdate(BaseModel):
    domain_code: str | None = None
    domain_name: str | None = None
    parent_domain_id: UUID | None = None
    description: str | None = None
    is_active: bool | None = None


class ResearchDomainOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    domain_id: UUID
    domain_code: str
    domain_name: str
    parent_domain_id: UUID | None
    description: str | None
    is_active: bool


# ── Researcher ────────────────────────────────────────────────────────────────

class ResearcherCreate(BaseModel):
    full_name: str
    email: str | None = None
    orcid: str | None = None
    department_id: UUID | None = None
    academic_title: str | None = None
    researcher_code: str | None = None
    is_internal: bool = True


class ResearcherUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    orcid: str | None = None
    department_id: UUID | None = None
    academic_title: str | None = None
    researcher_code: str | None = None
    is_internal: bool | None = None


class ResearcherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    researcher_id: UUID
    full_name: str
    email: str | None
    orcid: str | None
    department_id: UUID | None
    academic_title: str | None
    researcher_code: str | None
    is_internal: bool


# ── Keyword ───────────────────────────────────────────────────────────────────

class KeywordCreate(BaseModel):
    keyword_text: str
    normalized_text: str | None = None


class KeywordUpdate(BaseModel):
    keyword_text: str | None = None
    normalized_text: str | None = None


class KeywordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    keyword_id: UUID
    keyword_text: str
    normalized_text: str | None