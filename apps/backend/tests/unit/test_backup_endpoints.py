from datetime import datetime, timezone
from types import SimpleNamespace

from app.api.v1.endpoints import backup as backup_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps


class FakeDbSession:
    pass


def _override_db():
    async def _provider():
        yield FakeDbSession()

    return _provider


def _override_user(client, sample_user, role_code: str) -> None:
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _provider():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _provider


def test_super_admin_can_create_database_backup(client, sample_user, monkeypatch):
    _override_user(client, sample_user, "SUPER_ADMIN")
    client.app.dependency_overrides[get_db] = _override_db()
    captured = {}
    created_at = datetime.now(timezone.utc)

    async def _fake_create(db, *, actor_user_id):
        captured["db"] = db
        captured["actor_user_id"] = actor_user_id
        return {
            "filename": "rdms-test.dump",
            "size_bytes": 1024,
            "created_at": created_at,
        }

    monkeypatch.setattr(backup_endpoint.backup_service, "create_database_backup", _fake_create)

    response = client.post(f"{settings.API_V1_PREFIX}/backup/backups")

    assert response.status_code == 201
    assert response.json()["filename"] == "rdms-test.dump"
    assert response.json()["size_bytes"] == 1024
    assert captured["actor_user_id"] == sample_user.user_id
    assert isinstance(captured["db"], FakeDbSession)


def test_non_admin_cannot_create_database_backup(client, sample_user):
    _override_user(client, sample_user, "MANAGER")
    client.app.dependency_overrides[get_db] = _override_db()

    response = client.post(f"{settings.API_V1_PREFIX}/backup/backups")

    assert response.status_code == 403
