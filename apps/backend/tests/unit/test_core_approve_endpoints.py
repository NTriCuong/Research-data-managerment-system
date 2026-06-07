from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.dialects import postgresql

from app.api.v1.endpoints import core_approve as approve_endpoint
from app.api.v1.endpoints import search as search_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps
from app.services.core.core_approve_service import core_approve_service
from app.services.search.search_service import search_service


class _FakeDbSession:
    async def commit(self):
        return None


class _FakeSearchResult:
    def all(self):
        return []


class _CaptureSearchDbSession:
    def __init__(self):
        self.statement = None

    async def execute(self, statement):
        self.statement = statement
        return _FakeSearchResult()


def _fake_db_provider():
    async def _override_get_db():
        yield _FakeDbSession()

    return _override_get_db


def _override_user_with_role(client, sample_user, role_code: str):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user
    client.app.dependency_overrides[auth_deps.get_optional_current_active_user] = _override_current_active_user


def test_approver_can_list_pending_records(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "APPROVER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_list_pending(*_args, **_kwargs):
        return [
            {
                "staging_id": staging_id,
                "title": "Awaiting Approval",
                "output_type_id": uuid4(),
                "department_id": uuid4(),
                "year": 2026,
                "workflow_status": "pending_approval",
                "submitted_by": sample_user.user_id,
                "reviewed_by": sample_user.user_id,
                "submitted_at": None,
                "reviewed_at": None,
                "created_at": "2026-05-26T00:00:00Z",
                "updated_at": None,
            }
        ]

    monkeypatch.setattr(approve_endpoint.core_approve_service, "list_pending_approval_records", _fake_list_pending)

    response = client.get(f"{settings.API_V1_PREFIX}/core-approve/pending")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["staging_id"] == str(staging_id)
    assert body[0]["workflow_status"] == "pending_approval"


def test_approver_can_approve_record(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "APPROVER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    captured = {}

    async def _fake_approve(*_args, **kwargs):
        captured.update(kwargs)
        return {"message": "Phê duyệt và xuất bản bản ghi vào core thành công"}

    monkeypatch.setattr(approve_endpoint.core_approve_service, "approve_record", _fake_approve)

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/approve",
        json={
            "note": "Approved for publication",
            "access_level": "private",
            "file_access_levels": [{"file_id": str(staging_id), "access_level": "internal"}],
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Phê duyệt và xuất bản bản ghi vào core thành công"
    assert captured["payload"].access_level.value == "private"
    assert captured["payload"].file_access_levels[0].file_id == staging_id
    assert captured["payload"].file_access_levels[0].access_level.value == "internal"


def test_approver_can_reject_record(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "APPROVER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_reject(*_args, **_kwargs):
        return {"message": "Từ chối bản ghi thành công"}

    monkeypatch.setattr(approve_endpoint.core_approve_service, "reject_record", _fake_reject)

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/reject",
        json={"reason": "Insufficient evidence"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Từ chối bản ghi thành công"


def test_postgres_search_accessible_for_reviewer(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    research_id = uuid4()

    async def _fake_search(*_args, **_kwargs):
        return [
            {
                "research_id": research_id,
                "title": "PostgreSQL Search Benchmark",
                "year": 2026,
                "access_level": "public",
                "version_no": 2,
                "approved_at": "2026-05-26T00:00:00Z",
                "rank": 0.75,
            }
        ]

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(f"{settings.API_V1_PREFIX}/search/core?q=benchmark")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["research_id"] == str(research_id)


def test_postgres_search_strips_query_and_passes_pagination(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    captured = {}

    async def _fake_search(*args, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(
        f"{settings.API_V1_PREFIX}/search/core",
        params={"q": "  trí tuệ  ", "limit": 5, "offset": 2},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert captured["query"] == "trí tuệ"
    assert captured["limit"] == 5
    assert captured["offset"] == 2


def test_unauthenticated_user_can_search_core_records(client, monkeypatch):
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    async def _fake_search(*_args, **_kwargs):
        return []

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(f"{settings.API_V1_PREFIX}/search/core?q=benchmark")

    assert response.status_code == 200
    assert response.json() == []


def test_reject_record_requires_non_empty_reason(client, sample_user):
    _override_user_with_role(client, sample_user, "APPROVER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{uuid4()}/reject",
        json={"reason": ""},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_postgres_search_query_matches_srs_fields():
    db = _CaptureSearchDbSession()

    rows = await search_service.search_core_postgres(db, query="tri tue nhan tao", limit=10, offset=0)

    assert rows == []
    compiled_sql = str(
        db.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": False},
        )
    ).lower()
    assert "websearch_to_tsquery" in compiled_sql
    assert "unaccent" in compiled_sql
    assert "search_vector" in compiled_sql
    assert "research_objects.access_level =" in compiled_sql
    assert "description" in compiled_sql
    assert "identifier" in compiled_sql
    assert "research_object_authors" in compiled_sql
    assert "research_object_keywords" in compiled_sql
    assert "keywords" in compiled_sql
    assert "research_object_domains" in compiled_sql
    assert "research_domains" in compiled_sql


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("role_code", "expected_sql"),
    [
        ("DATA_ENTRY", "research_objects.source_staging_id in"),
        ("REVIEWER", "research_objects.access_level in"),
        ("APPROVER", "workflow_status"),
    ],
)
async def test_postgres_search_applies_role_access_rules(sample_user, role_code, expected_sql):
    sample_user.role = SimpleNamespace(role_code=role_code)
    db = _CaptureSearchDbSession()

    await search_service.search_core_postgres(
        db,
        query="benchmark",
        limit=10,
        offset=0,
        current_user=sample_user,
    )

    compiled_sql = str(db.statement.compile(dialect=postgresql.dialect())).lower()
    assert expected_sql in compiled_sql


def test_data_entry_cannot_approve(client, sample_user):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/approve",
        json={"note": "Should fail"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Bạn không có đủ quyền để thực hiện thao tác này"
