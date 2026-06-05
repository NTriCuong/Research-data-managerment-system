import hashlib
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.models.enum import AccessLevel
from app.services.storage import file_service as file_service_module
from app.services.storage.file_service import MAX_UPLOAD_SIZE_BYTES, FileService

pytestmark = pytest.mark.asyncio


class ChunkedUpload:
    def __init__(self, chunks: list[bytes], *, filename: str = "evidence.pdf", content_type: str = "application/pdf") -> None:
        self._chunks = chunks
        self.filename = filename
        self.content_type = content_type

    async def read(self, _size: int = -1) -> bytes:
        if not self._chunks:
            return b""
        return self._chunks.pop(0)


async def test_prepare_file_upload_streams_fileobj_to_r2(monkeypatch):
    chunks = [b"hello", b"-", b"world"]
    uploaded = {}

    def _fake_upload(*, object_key, fileobj, content_type):
        uploaded["object_key"] = object_key
        uploaded["content_type"] = content_type
        uploaded["data"] = fileobj.read()
        return SimpleNamespace(storage_path=object_key, public_url=None)

    monkeypatch.setattr(file_service_module, "upload_fileobj_to_r2", _fake_upload)

    result = await FileService().prepare_file_upload(
        staging_id=uuid4(),
        file=ChunkedUpload(chunks.copy()),
        access_level="internal",
    )

    expected_data = b"hello-world"
    assert uploaded["data"] == expected_data
    assert uploaded["content_type"] == "application/pdf"
    assert uploaded["object_key"] == result["storage_path"]
    assert result["file_size_bytes"] == len(expected_data)
    assert result["checksum_sha256"] == hashlib.sha256(expected_data).hexdigest()
    assert result["access_level"] == AccessLevel.internal


async def test_prepare_file_upload_rejects_over_50mb_before_r2(monkeypatch):
    calls = {"count": 0}

    def _fake_upload(**_kwargs):
        calls["count"] += 1

    monkeypatch.setattr(file_service_module, "upload_fileobj_to_r2", _fake_upload)

    upload = ChunkedUpload([b"a" * MAX_UPLOAD_SIZE_BYTES, b"b"])

    with pytest.raises(HTTPException) as exc_info:
        await FileService().prepare_file_upload(
            staging_id=uuid4(),
            file=upload,
            access_level="internal",
        )

    assert exc_info.value.status_code == status.HTTP_413_CONTENT_TOO_LARGE
    assert exc_info.value.detail == "File size exceeds 50MB limit"
    assert calls["count"] == 0
