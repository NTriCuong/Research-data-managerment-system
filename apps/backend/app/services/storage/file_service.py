import asyncio
import hashlib
from pathlib import Path
from typing import BinaryIO
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
CHECKSUM_CHUNK_SIZE_BYTES = 1024 * 1024

ALLOWED_MIME_TYPES_BY_EXTENSION: dict[str, frozenset[str]] = {
    ".csv": frozenset({"text/csv", "application/csv", "text/plain"}),
    ".doc": frozenset({"application/msword"}),
    ".docx": frozenset({"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}),
    ".jpeg": frozenset({"image/jpeg"}),
    ".jpg": frozenset({"image/jpeg"}),
    ".pdf": frozenset({"application/pdf"}),
    ".png": frozenset({"image/png"}),
    ".txt": frozenset({"text/plain"}),
    ".xls": frozenset({"application/vnd.ms-excel"}),
    ".xlsx": frozenset({"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}),
    ".zip": frozenset({"application/zip", "application/x-zip-compressed"}),
}


class FileService:
    async def prepare_file_upload(
        self,
        *,
        staging_id: UUID,
        file: IncomingFile,
        access_level: str,
    ) -> dict:
        original_filename = file.filename
        file_extension = Path(original_filename).suffix.lower()
        mime_type = file.content_type.lower().split(";", maxsplit=1)[0].strip()
        self._validate_file_type(file_extension=file_extension, mime_type=mime_type)

        stored_filename = f"{uuid4().hex}{file_extension}"
        storage_key = f"staging/{staging_id}/{stored_filename}"

        try:
            access_level_enum = AccessLevel(access_level)
        except ValueError as exc:
            raise BadRequestException("access_level không hợp lệ") from exc

        try:
            file_size_bytes, checksum_sha256, upload_result = await asyncio.to_thread(
                self._scan_and_upload,
                object_key=storage_key,
                fileobj=file.fileobj,
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
            "checksum_sha256": checksum_sha256,
            "access_level": access_level_enum,
        }

    @staticmethod
    def _validate_file_type(*, file_extension: str, mime_type: str) -> None:
        allowed_mime_types = ALLOWED_MIME_TYPES_BY_EXTENSION.get(file_extension)
        if allowed_mime_types is None:
            raise BadRequestException("Phần mở rộng tệp không được hỗ trợ")
        if mime_type not in allowed_mime_types:
            raise BadRequestException("MIME type không khớp với phần mở rộng tệp")

    @staticmethod
    def _scan_and_upload(*, object_key: str, fileobj: BinaryIO, content_type: str):
        checksum = hashlib.sha256()
        file_size_bytes = 0
        fileobj.seek(0)

        while chunk := fileobj.read(CHECKSUM_CHUNK_SIZE_BYTES):
            file_size_bytes += len(chunk)
            if file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
                raise PayloadTooLargeException("Kích thước tệp vượt quá giới hạn 50MB")
            checksum.update(chunk)

        if file_size_bytes == 0:
            raise BadRequestException("Tệp không được để trống")

        fileobj.seek(0)
        upload_result = upload_fileobj_to_r2(
            object_key=object_key,
            fileobj=fileobj,
            content_type=content_type,
        )
        return file_size_bytes, checksum.hexdigest(), upload_result


file_service = FileService()
