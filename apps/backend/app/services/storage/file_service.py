import asyncio
import hashlib
from pathlib import Path
from uuid import UUID
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.models.enum import AccessLevel
from app.services.storage.r2_storage import upload_bytes_to_r2


class FileService:
    async def prepare_file_upload(
        self,
        *,
        staging_id: UUID,
        file: UploadFile,
        access_level: str,
    ) -> dict:
        file_bytes = await file.read()
        file_size_bytes = len(file_bytes)
        if file_size_bytes > 50 * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds 50MB limit")
        if file_size_bytes == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty")

        original_filename = file.filename or "uploaded-file"
        file_extension = Path(original_filename).suffix.lower() or None
        stored_filename = f"{uuid4().hex}{file_extension or ''}"
        storage_key = f"staging/{staging_id}/{stored_filename}"
        mime_type = file.content_type or "application/octet-stream"
        checksum_sha256 = hashlib.sha256(file_bytes).hexdigest()

        try:
            access_level_enum = AccessLevel(access_level)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access_level") from exc

        try:
            upload_result = await asyncio.to_thread(
                upload_bytes_to_r2,
                object_key=storage_key,
                data=file_bytes,
                content_type=mime_type,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to upload file to cloud storage") from exc

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


file_service = FileService()
