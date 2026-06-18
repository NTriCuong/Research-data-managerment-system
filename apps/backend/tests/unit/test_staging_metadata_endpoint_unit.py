from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints import staging_metadata as metadata_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps


class _FakeDbSession:
    def __init__(self):
        self.commit_count = 0

    async def commit(self):
        self.commit_count += 1


def _fake_db_provider(db=None):
    fake_db = db or _FakeDbSession()

    async def _override_get_db():
        yield fake_db

    return _override_get_db


def _override_user_with_role(client, sample_user, role_code: str):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user


def _staging_payload(staging_id, sample_user, workflow_status="draft"):
    return {
        "staging_id": staging_id,
        "title": "Endpoint coverage record",
        "output_type_id": uuid4(),
        "department_id": uuid4(),
        "year": 2026,
        "workflow_status": workflow_status,
        "access_level": "internal",
        "source_core_research_id": None,
        "update_reason": None,
        "metadata_quality_score": "85.50",
        "created_by": sample_user.user_id,
        "submitted_by": None,
        "submitted_at": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None,
    }


def _file_payload(staging_id, sample_user, filename="evidence.pdf"):
    return {
        "file_id": uuid4(),
        "staging_id": staging_id,
        "original_filename": filename,
        "stored_filename": f"{uuid4()}-{filename}",
        "storage_path": f"staging/{staging_id}/{filename}",
        "mime_type": "application/pdf",
        "file_extension": ".pdf",
        "file_size_bytes": 11,
        "checksum_sha256": "a" * 64,
        "file_status": "active",
        "uploaded_by": sample_user.user_id,
        "uploaded_at": datetime.now(timezone.utc),
        "access_level": "internal",
    }


def test_data_entry_can_create_staging_record(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    db = _FakeDbSession()
    client.app.dependency_overrides[get_db] = _fake_db_provider(db)
    staging_id = uuid4()
    domain_id = uuid4()
    keyword_id = uuid4()
    researcher_id = uuid4()
    captured = {}

    async def _fake_create(db_arg, *, payload, current_user):
        captured["db"] = db_arg
        captured["payload"] = payload
        captured["current_user"] = current_user
        return _staging_payload(staging_id, sample_user)

    monkeypatch.setattr(metadata_endpoint.staging_service, "create_staging_research_object", _fake_create)

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata",
        json={
            "title": "Endpoint coverage record",
            "output_type_id": str(uuid4()),
            "department_id": str(uuid4()),
            "year": 2026,
            "access_level": "internal",
            "domain_ids": [str(domain_id)],
            "keyword_ids": [str(keyword_id)],
            "authors": [{"researcher_id": str(researcher_id), "author_order": 1}],
        },
    )

    assert response.status_code == 201
    assert response.json()["staging_id"] == str(staging_id)
    assert captured["db"] is db
    assert captured["payload"].title == "Endpoint coverage record"
    assert captured["payload"].domain_ids == [domain_id]
    assert captured["payload"].keyword_ids == [keyword_id]
    assert captured["payload"].authors[0].researcher_id == researcher_id
    assert captured["payload"].authors[0].full_name is None
    assert captured["current_user"] is sample_user
    assert db.commit_count == 0


def test_manager_can_list_all_staging_records_with_filters(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "MANAGER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()
    captured = {}

    async def _fake_list_all(*args, **kwargs):
        captured.update(kwargs)
        return [_staging_payload(staging_id, sample_user, workflow_status="pending_review")]

    monkeypatch.setattr(metadata_endpoint.staging_service, "list_all_staging_records", _fake_list_all)

    response = client.get(
        f"{settings.API_V1_PREFIX}/staging-metadata",
        params={"workflow_status": "pending_review", "limit": 7, "offset": 3},
    )

    assert response.status_code == 200
    assert response.json()[0]["workflow_status"] == "pending_review"
    assert captured["workflow_status"].value == "pending_review"
    assert captured["limit"] == 7
    assert captured["offset"] == 3


def test_submit_for_review_returns_message_without_endpoint_commit(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    db = _FakeDbSession()
    client.app.dependency_overrides[get_db] = _fake_db_provider(db)
    staging_id = uuid4()
    captured = {}

    async def _fake_submit(*args, **kwargs):
        captured.update(kwargs)
        return {"message": "Gửi xét duyệt thành công"}

    monkeypatch.setattr(metadata_endpoint.staging_service, "submit_for_review", _fake_submit)

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata/{staging_id}/submit",
        json={"note": "ready"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Gửi xét duyệt thành công"
    assert captured["staging_id"] == staging_id
    assert captured["payload"].note == "ready"
    assert db.commit_count == 0


def test_list_workflow_history_passes_pagination(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "MANAGER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()
    workflow_id = uuid4()
    captured = {}

    async def _fake_history(*args, **kwargs):
        captured.update(kwargs)
        return [
            {
                "workflow_id": workflow_id,
                "staging_id": staging_id,
                "research_id": None,
                "from_status": "draft",
                "to_status": "pending_review",
                "action_code": "SUBMIT_FOR_REVIEW",
                "action_note": "ready",
                "performed_by": sample_user.user_id,
                "performed_at": datetime.now(timezone.utc),
            }
        ]

    monkeypatch.setattr(metadata_endpoint.staging_service, "list_staging_workflow_history", _fake_history)

    response = client.get(
        f"{settings.API_V1_PREFIX}/staging-metadata/{staging_id}/workflow-history",
        params={"limit": 9, "offset": 4},
    )

    assert response.status_code == 200
    assert response.json()[0]["action_code"] == "SUBMIT_FOR_REVIEW"
    assert captured["staging_id"] == staging_id
    assert captured["limit"] == 9
    assert captured["offset"] == 4


def test_upload_endpoint_passes_file_without_access_level_to_service(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    db = _FakeDbSession()
    client.app.dependency_overrides[get_db] = _fake_db_provider(db)
    staging_id = uuid4()
    captured = {}

    async def _fake_upload(*args, **kwargs):
        captured.update(kwargs)
        captured["file_bytes"] = kwargs["file"].fileobj.read()
        kwargs["file"].fileobj.seek(0)
        return _file_payload(staging_id, sample_user)

    monkeypatch.setattr(metadata_endpoint.staging_service, "create_staging_file_metadata", _fake_upload)

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata/{staging_id}/files",
        files={"file": ("evidence.pdf", b"pdf-content", "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json()["original_filename"] == "evidence.pdf"
    assert captured["staging_id"] == staging_id
    assert "access_level" not in captured
    assert captured["file"].filename == "evidence.pdf"
    assert captured["file_bytes"] == b"pdf-content"
    assert db.commit_count == 0


def test_delete_staging_file_does_not_commit_in_endpoint(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    db = _FakeDbSession()
    client.app.dependency_overrides[get_db] = _fake_db_provider(db)
    staging_id = uuid4()
    file_id = uuid4()
    captured = {}

    async def _fake_delete(*args, **kwargs):
        captured.update(kwargs)
        return {"message": "Xóa tệp thành công"}

    monkeypatch.setattr(metadata_endpoint.staging_service, "delete_staging_file", _fake_delete)

    response = client.delete(f"{settings.API_V1_PREFIX}/staging-metadata/{staging_id}/files/{file_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Xóa tệp thành công"
    assert captured["staging_id"] == staging_id
    assert captured["file_id"] == file_id
    assert db.commit_count == 0


def test_reviewer_cannot_upload_staging_file(client, sample_user):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata/{uuid4()}/files",
        files={"file": ("blocked.pdf", b"blocked", "application/pdf")},
        data={"access_level": "internal"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Bạn không có đủ quyền để thực hiện thao tác này"
