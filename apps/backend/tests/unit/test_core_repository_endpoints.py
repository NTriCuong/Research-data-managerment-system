from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints import core_repository as core_repository_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps


class _FakeDbSession:
    pass


def _override_user_and_db(client, sample_user, role_code: str, fake_db):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    async def _override_get_db():
        yield fake_db

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user
    client.app.dependency_overrides[get_db] = _override_get_db


def test_data_entry_can_list_own_published_records(client, sample_user, monkeypatch):
    sample_user.role = SimpleNamespace(role_code="DATA_ENTRY")
    fake_db = _FakeDbSession()
    research_id = uuid4()
    captured = {}

    async def _override_current_active_user():
        return sample_user

    async def _override_get_db():
        yield fake_db

    async def _fake_list_my_core_records(*args, **kwargs):
        captured["db"] = args[0]
        captured.update(kwargs)
        now = datetime.now(timezone.utc)
        return [
            {
                "research_id": research_id,
                "title": "Nghiên cứu đã công bố",
                "output_type_id": uuid4(),
                "department_id": uuid4(),
                "year": 2026,
                "access_level": "public",
                "metadata_quality_score": "90.00",
                "view_count": 10,
                "download_count": 2,
                "version_no": 2,
                "is_current": True,
                "approved_by": uuid4(),
                "approved_at": now,
                "created_at": now,
                "updated_at": now,
            }
        ]

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user
    client.app.dependency_overrides[get_db] = _override_get_db
    monkeypatch.setattr(
        core_repository_endpoint.core_repository_service,
        "list_my_core_records",
        _fake_list_my_core_records,
    )

    response = client.get(
        f"{settings.API_V1_PREFIX}/core-repository/mine",
        params={"limit": 12, "offset": 3},
    )

    assert response.status_code == 200
    assert response.json()[0]["research_id"] == str(research_id)
    assert response.json()[0]["version_no"] == 2
    assert captured["db"] is fake_db
    assert captured["creator_id"] == sample_user.user_id
    assert captured["limit"] == 12
    assert captured["offset"] == 3


def test_approver_can_update_approved_file_access_level(client, sample_user, monkeypatch):
    fake_db = _FakeDbSession()
    research_id = uuid4()
    file_id = uuid4()
    now = datetime.now(timezone.utc)
    captured = {}
    _override_user_and_db(client, sample_user, "APPROVER", fake_db)

    async def _fake_update(*args, **kwargs):
        captured["db"] = args[0]
        captured.update(kwargs)
        return {
            "file_id": file_id,
            "research_id": research_id,
            "original_filename": "minh-chung.pdf",
            "stored_filename": "stored.pdf",
            "storage_path": "core/file.pdf",
            "mime_type": "application/pdf",
            "file_extension": ".pdf",
            "file_size_bytes": 1024,
            "checksum_sha256": None,
            "file_status": "active",
            "uploaded_by": sample_user.user_id,
            "uploaded_at": now,
            "access_level": "public",
        }

    monkeypatch.setattr(
        core_repository_endpoint.core_repository_service,
        "update_core_file_access_level",
        _fake_update,
    )

    response = client.patch(
        f"{settings.API_V1_PREFIX}/core-repository/{research_id}/files/{file_id}/access-level",
        json={"access_level": "public"},
    )

    assert response.status_code == 200
    assert response.json()["access_level"] == "public"
    assert captured["db"] is fake_db
    assert captured["research_id"] == research_id
    assert captured["file_id"] == file_id
    assert captured["access_level"].value == "public"
    assert captured["current_user"] is sample_user


def test_reviewer_cannot_update_approved_file_access_level(client, sample_user):
    _override_user_and_db(client, sample_user, "REVIEWER", _FakeDbSession())
    response = client.patch(
        f"{settings.API_V1_PREFIX}/core-repository/{uuid4()}/files/{uuid4()}/access-level",
        json={"access_level": "public"},
    )
    assert response.status_code == 403


def test_approver_can_update_approved_research_access_level(client, sample_user, monkeypatch):
    fake_db = _FakeDbSession()
    research_id = uuid4()
    now = datetime.now(timezone.utc)
    captured = {}
    _override_user_and_db(client, sample_user, "APPROVER", fake_db)

    async def _fake_update(*args, **kwargs):
        captured["db"] = args[0]
        captured.update(kwargs)
        return {
            "research_id": research_id,
            "title": "Nghiên cứu đã duyệt",
            "output_type_id": uuid4(),
            "department_id": uuid4(),
            "year": 2026,
            "access_level": "internal",
            "metadata_quality_score": None,
            "view_count": 0,
            "download_count": 0,
            "version_no": 1,
            "is_current": True,
            "approved_by": sample_user.user_id,
            "approved_at": now,
            "created_at": now,
            "updated_at": now,
        }

    monkeypatch.setattr(
        core_repository_endpoint.core_repository_service,
        "update_core_research_access_level",
        _fake_update,
    )

    response = client.patch(
        f"{settings.API_V1_PREFIX}/core-repository/{research_id}/access-level",
        json={"access_level": "internal"},
    )

    assert response.status_code == 200
    assert response.json()["access_level"] == "internal"
    assert captured["db"] is fake_db
    assert captured["research_id"] == research_id
    assert captured["access_level"].value == "internal"
    assert captured["current_user"] is sample_user
