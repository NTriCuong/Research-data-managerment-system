from __future__ import annotations

from dataclasses import dataclass

import boto3
from botocore.client import BaseClient

from app.core.config import settings


@dataclass(frozen=True)
class R2UploadResult:
    storage_path: str
    public_url: str | None


def _require_r2_settings() -> tuple[str, str, str, str]:
    if not settings.CLOUDFLARE_R2_ACCOUNT_ID:
        raise RuntimeError("Missing CLOUDFLARE_R2_ACCOUNT_ID")
    if not settings.CLOUDFLARE_R2_ACCESS_KEY_ID:
        raise RuntimeError("Missing CLOUDFLARE_R2_ACCESS_KEY_ID")
    if not settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY:
        raise RuntimeError("Missing CLOUDFLARE_R2_SECRET_ACCESS_KEY")
    if not settings.CLOUDFLARE_R2_BUCKET_NAME:
        raise RuntimeError("Missing CLOUDFLARE_R2_BUCKET_NAME")
    return (
        settings.CLOUDFLARE_R2_ACCOUNT_ID,
        settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
        settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
        settings.CLOUDFLARE_R2_BUCKET_NAME,
    )


def _build_s3_client(account_id: str, access_key_id: str, secret_access_key: str) -> BaseClient:
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name="auto",
    )


def upload_bytes_to_r2(*, object_key: str, data: bytes, content_type: str) -> R2UploadResult:
    account_id, access_key_id, secret_access_key, bucket_name = _require_r2_settings()
    s3_client = _build_s3_client(account_id, access_key_id, secret_access_key)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )

    public_url: str | None = None
    if settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
        base = settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip("/")
        public_url = f"{base}/{object_key}"

    return R2UploadResult(storage_path=object_key, public_url=public_url)


def upload_fileobj_to_r2(*, object_key: str, fileobj, content_type: str) -> R2UploadResult:
    account_id, access_key_id, secret_access_key, bucket_name = _require_r2_settings()
    s3_client = _build_s3_client(account_id, access_key_id, secret_access_key)
    fileobj.seek(0)
    s3_client.upload_fileobj(
        fileobj,
        bucket_name,
        object_key,
        ExtraArgs={"ContentType": content_type},
    )

    public_url: str | None = None
    if settings.CLOUDFLARE_R2_PUBLIC_BASE_URL:
        base = settings.CLOUDFLARE_R2_PUBLIC_BASE_URL.rstrip("/")
        public_url = f"{base}/{object_key}"

    return R2UploadResult(storage_path=object_key, public_url=public_url)
