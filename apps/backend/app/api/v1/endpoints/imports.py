from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_roles
from app.database.session import get_db
from app.models.auth.user import User
from app.schemas.files import IncomingFile
from app.schemas.imports import StagingExcelImportResponse
from app.services.imports.staging_excel_import_service import staging_excel_import_service

router = APIRouter()

ALLOWED_IMPORT_ROLES = ("SUPER_ADMIN", "DATA_ENTRY")


@router.post("/staging/excel", response_model=StagingExcelImportResponse)
async def import_staging_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(*ALLOWED_IMPORT_ROLES)),
    db: AsyncSession = Depends(get_db),
) -> StagingExcelImportResponse:
    incoming_file = IncomingFile(
        filename=file.filename or "import.xlsx",
        content_type=file.content_type or "application/octet-stream",
        content=await file.read(),
    )
    return await staging_excel_import_service.import_workbook(
        db,
        file=incoming_file,
        current_user=current_user,
    )
