from uuid import UUID

from pydantic import BaseModel


class ImportRowError(BaseModel):
    sheet: str
    row_number: int
    message: str


class StagingExcelImportResponse(BaseModel):
    imported_projects: int
    imported_file_attachments: int
    staging_ids: list[UUID]
    errors: list[ImportRowError] = []
