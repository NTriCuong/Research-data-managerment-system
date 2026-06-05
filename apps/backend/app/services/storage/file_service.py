import asyncio
import hashlib
import tempfile
from pathlib import Path
from uuid import UUID
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.models.enum import AccessLevel
from app.services.storage.r2_storage import upload_fileobj_to_r2


MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024
UPLOAD_CHUNK_SIZE_BYTES = 1024 * 1024


class FileService:
    async def prepare_file_upload(
        self,
        *,
        staging_id: UUID,
        file: UploadFile,
        access_level: str,
    ) -> dict:
        original_filename = file.filename or "uploaded-file"
        file_extension = Path(original_filename).suffix.lower() or None
        stored_filename = f"{uuid4().hex}{file_extension or ''}"
        storage_key = f"staging/{staging_id}/{stored_filename}"
        mime_type = file.content_type or "application/octet-stream"

        try:
            access_level_enum = AccessLevel(access_level)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access_level") from exc

        checksum = hashlib.sha256()
        file_size_bytes = 0
        temp_file = tempfile.TemporaryFile()
        try:
            while chunk := await file.read(UPLOAD_CHUNK_SIZE_BYTES):
                file_size_bytes += len(chunk)
                if file_size_bytes > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                        detail="File size exceeds 50MB limit",
                    )
                checksum.update(chunk)
                temp_file.write(chunk)

            if file_size_bytes == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty")

            temp_file.seek(0)
            upload_result = await asyncio.to_thread(
                upload_fileobj_to_r2,
                object_key=storage_key,
                fileobj=temp_file,
                content_type=mime_type,
            )
        except HTTPException:
            raise
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to upload file to cloud storage") from exc
        finally:
            temp_file.close()

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
