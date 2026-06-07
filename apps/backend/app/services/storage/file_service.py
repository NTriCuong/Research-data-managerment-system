import asyncio
import hashlib
from io import BytesIO
from pathlib import Path
from uuid import UUID
from uuid import uuid4

from app.core.exceptions import (
    AppException,
    BadRequestException,
    ExternalServiceException,
    InternalServerException,
    PayloadTooLargeException,
)
from app.models.enum import AccessLevel
from app.schemas.files import IncomingFile
from app.services.storage.r2_storage import upload_fileobj_to_r2


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024


class FileService:
    async def prepare_file_upload(
        self,
        *,
        staging_id: UUID,
        file: IncomingFile,
        access_level: str,
    ) -> dict:
        original_filename = file.filename
        file_extension = Path(original_filename).suffix.lower() or None
        stored_filename = f"{uuid4().hex}{file_extension or ''}"
        storage_key = f"staging/{staging_id}/{stored_filename}"
        mime_type = file.content_type

        try:
            access_level_enum = AccessLevel(access_level)
        except ValueError as exc:
            raise BadRequestException("access_level không hợp lệ") from exc

        file_size_bytes = len(file.content)
        if file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
            raise PayloadTooLargeException("Kích thước tệp vượt quá giới hạn 50MB")
        if file_size_bytes == 0:
            raise BadRequestException("Tệp không được để trống")

        checksum = hashlib.sha256(file.content)
        try:
            upload_result = await asyncio.to_thread(
                upload_fileobj_to_r2,
                object_key=storage_key,
                fileobj=BytesIO(file.content),
                content_type=mime_type,
            )
        except AppException:
            raise
        except RuntimeError as exc:
            raise InternalServerException("Có lỗi xảy ra khi xử lý tệp") from exc
        except Exception as exc:
            raise ExternalServiceException("Tải tệp lên kho lưu trữ đám mây thất bại") from exc
        return {
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "storage_path": upload_result.storage_path,
            "mime_type": mime_type,
            "file_extension": file_extension,
            "file_size_bytes": file_size_bytes,
            "checksum_sha256": checksum.hexdigest(),
            "access_level": access_level_enum,
        }


file_service = FileService()
