from pydantic import BaseModel


class TotalCoreRepositoriesOut(BaseModel):
    total_core_repositories: int


class PendingStatusOut(BaseModel):
    pending_review: int
    pending_approval: int
    total_pending: int


class TotalResearchersOut(BaseModel):
    total_researchers: int
    internal: int
    external: int


class MetadataQualityOut(BaseModel):
    avg_score: float
    min_score: float
    max_score: float
    total_records: int


class StatusBreakdownItem(BaseModel):
    status: str
    count: int


class TopDepartmentItem(BaseModel):
    department_name: str
    count: int
