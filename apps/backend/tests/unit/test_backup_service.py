import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import ExternalServiceException
from app.services.backup import backup_service as backup_service_module


class FakeProcess:
    def __init__(self, returncode: int = 0, stderr: bytes = b"") -> None:
        self.returncode = returncode
        self.stderr = stderr

    async def communicate(self):
        return b"", self.stderr


def test_backup_service_runs_pg_dump_without_password_in_command(tmp_path, monkeypatch):
    captured = {}
    actor_user_id = uuid4()
    fake_db = SimpleNamespace()

    async def _fake_exec(*command, **kwargs):
        captured["command"] = command
        captured["env"] = kwargs["env"]
        output_path = command[command.index("--file") + 1]
        with open(output_path, "wb") as backup_file:
            backup_file.write(b"backup-content")
        return FakeProcess()

    async def _fake_write_log(_db, **kwargs):
        captured["audit"] = kwargs

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+asyncpg://backup_user:secret-password@db.example:5433/rdms",
    )
    monkeypatch.setattr(backup_service_module.settings, "BACKUP_DIRECTORY", tmp_path)
    monkeypatch.setattr(backup_service_module.settings, "PG_DUMP_PATH", "pg_dump")
    monkeypatch.setattr(backup_service_module.asyncio, "create_subprocess_exec", _fake_exec)
    monkeypatch.setattr(backup_service_module.audit_service, "write_log", _fake_write_log)

    result = asyncio.run(
        backup_service_module.backup_service.create_database_backup(
            fake_db,
            actor_user_id=actor_user_id,
        )
    )

    assert result.size_bytes == len(b"backup-content")
    assert (tmp_path / result.filename).exists()
    assert "secret-password" not in captured["command"]
    assert captured["env"]["PGPASSWORD"] == "secret-password"
    assert captured["audit"]["actor_user_id"] == actor_user_id
    assert captured["audit"]["action_code"] == "ADMIN_CREATE_DATABASE_BACKUP"


def test_backup_service_removes_partial_file_when_pg_dump_fails(tmp_path, monkeypatch):
    async def _fake_exec(*command, **_kwargs):
        output_path = command[command.index("--file") + 1]
        with open(output_path, "wb") as backup_file:
            backup_file.write(b"partial")
        return FakeProcess(returncode=1, stderr=b"connection refused")

    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:password@db/rdms")
    monkeypatch.setattr(backup_service_module.settings, "BACKUP_DIRECTORY", tmp_path)
    monkeypatch.setattr(backup_service_module.asyncio, "create_subprocess_exec", _fake_exec)

    with pytest.raises(ExternalServiceException, match="connection refused"):
        asyncio.run(
            backup_service_module.backup_service.create_database_backup(
                SimpleNamespace(),
                actor_user_id=uuid4(),
            )
        )

    assert list(tmp_path.iterdir()) == []
