import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConfigurationException, ExternalServiceException
from app.schemas.backup import BackupOut
from app.services.logs.audit_service import audit_service


class BackupService:
    async def create_database_backup(
        self,
        db: AsyncSession,
        *,
        actor_user_id: UUID,
    ) -> BackupOut:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ConfigurationException("DATABASE_URL chưa được cấu hình")

        backup_directory = Path(settings.BACKUP_DIRECTORY).resolve()
        backup_directory.mkdir(parents=True, exist_ok=True)

        created_at = datetime.now(timezone.utc)
        filename = f"rdms-{created_at.strftime('%Y%m%dT%H%M%S%fZ')}.dump"
        backup_path = backup_directory / filename
        url = make_url(database_url)

        command = [
            settings.PG_DUMP_PATH,
            "--format=custom",
            "--no-password",
            "--file",
            str(backup_path),
        ]
        if url.host:
            command.extend(["--host", url.host])
        if url.port:
            command.extend(["--port", str(url.port)])
        if url.username:
            command.extend(["--username", url.username])
        if url.database:
            command.extend(["--dbname", url.database])

        process_env = os.environ.copy()
        if url.password:
            process_env["PGPASSWORD"] = url.password

        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env,
            )
        except FileNotFoundError as exc:
            raise ConfigurationException(
                f"Không tìm thấy công cụ pg_dump tại '{settings.PG_DUMP_PATH}'"
            ) from exc

        _, stderr = await process.communicate()
        if process.returncode != 0:
            backup_path.unlink(missing_ok=True)
            error_detail = stderr.decode("utf-8", errors="replace").strip()
            raise ExternalServiceException(
                f"Không thể tạo bản backup PostgreSQL: {error_detail or 'pg_dump thất bại'}"
            )

        result = BackupOut(
            filename=filename,
            size_bytes=backup_path.stat().st_size,
            created_at=created_at,
        )
        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="ADMIN_CREATE_DATABASE_BACKUP",
            target_schema="system",
            target_table="database_backups",
            new_value={
                "filename": result.filename,
                "size_bytes": result.size_bytes,
            },
            message="Super Admin created a PostgreSQL database backup",
        )
        return result


backup_service = BackupService()
