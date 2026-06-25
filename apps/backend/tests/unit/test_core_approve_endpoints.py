from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.dialects import postgresql

from app.api.v1.endpoints import core_approve as approve_endpoint
from app.api.v1.endpoints import search as search_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.models.core.core_metadata_version import CoreMetadataVersion
from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import AccessLevel, AuthorRole, WorkflowStatus
from app.schemas.core_approve import ApproveRequest
from app.services.auth import deps as auth_deps
from app.services.core import core_approve_service as approve_service_module
from app.services.core.core_approve_service import core_approve_service
from app.services.search.search_service import search_service


class _FakeDbSession:
    async def commit(self):
        return None


class _FakeSearchResult:
    def scalar_one(self):
        return 0

    def all(self):
        return []


class _CaptureSearchDbSession:
    def __init__(self):
        self.statement = None
        self.statements = []

    async def execute(self, statement):
        self.statement = statement
        self.statements.append(statement)
        return _FakeSearchResult()


class _ServiceFakeDbSession:
    def __init__(self):
        self.added = []
        self.executed = []

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        for item in self.added:
            if isinstance(item, CoreResearchObject) and item.research_id is None:
                item.research_id = uuid4()
        return None

    async def execute(self, statement, params=None):
        self.executed.append((statement, params))
        return _FakeSearchResult()


class _FakeCoreApproveRepository:
    staging_obj = None
    core_obj = None

    def __init__(self, _db):
        pass

    async def get_staging_by_id(self, _staging_id, *, with_relations=False):
        return self.staging_obj

    async def get_core_by_id(self, _research_id, *, with_relations=False):
        return self.core_obj


def _relation(**values):
    return SimpleNamespace(**values)


def _pending_staging_record(**overrides):
    values = {
        "staging_id": uuid4(),
        "source_core_research_id": None,
        "deleted_at": None,
        "workflow_status": WorkflowStatus.pending_approval,
        "title": "Approved title",
        "description": "Description",
        "abstract": "Abstract",
        "output_type_id": uuid4(),
        "department_id": uuid4(),
        "year": 2026,
        "start_date": None,
        "end_date": None,
        "date_issued": None,
        "publisher": None,
        "language": "vi",
        "identifier": "RDMS-001",
        "external_url": None,
        "source": None,
        "relation": None,
        "coverage": None,
        "rights": None,
        "access_level": AccessLevel.internal,
        "metadata_quality_score": None,
        "metadata_quality_detail": None,
        "update_reason": None,
        "authors": [
            _relation(
                researcher_id=uuid4(),
                full_name="Nguyen Van A",
                email="a@example.com",
                affiliation="RDMS",
                author_order=1,
                author_role=AuthorRole.creator,
            )
        ],
        "domains": [_relation(domain_id=uuid4())],
        "keywords": [_relation(keyword_id=uuid4())],
        "file_attachments": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _approved_core_record(**overrides):
    values = {
        "research_id": uuid4(),
        "deleted_at": None,
        "source_staging_id": uuid4(),
        "title": "Original title",
        "description": "Old description",
        "abstract": "Old abstract",
        "output_type_id": uuid4(),
        "department_id": uuid4(),
        "year": 2025,
        "start_date": None,
        "end_date": None,
        "date_issued": None,
        "publisher": None,
        "language": "vi",
        "identifier": "RDMS-001",
        "external_url": None,
        "source": None,
        "relation": None,
        "coverage": None,
        "rights": None,
        "access_level": AccessLevel.internal,
        "version_no": 1,
        "authors": [],
        "domains": [],
        "keywords": [],
        "file_attachments": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.fixture
def no_log_side_effects(monkeypatch):
    async def _noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(approve_service_module.workflow_service, "write_history", _noop)
    monkeypatch.setattr(approve_service_module.audit_service, "write_log", _noop)


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
                "access_level": "internal",
                "metadata_quality_score": None,
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


@pytest.mark.anyio
async def test_approve_new_record_creates_initial_metadata_version(sample_user, monkeypatch, no_log_side_effects):
    staging_obj = _pending_staging_record(title="First published title")
    _FakeCoreApproveRepository.staging_obj = staging_obj
    _FakeCoreApproveRepository.core_obj = None
    monkeypatch.setattr(approve_service_module, "CoreApproveRepository", _FakeCoreApproveRepository)
    db = _ServiceFakeDbSession()

    await core_approve_service.approve_record(
        db,
        staging_id=staging_obj.staging_id,
        payload=ApproveRequest(note="Approve initial version", access_level=AccessLevel.public),
        current_user=sample_user,
    )

    versions = [item for item in db.added if isinstance(item, CoreMetadataVersion)]
    assert len(versions) == 1
    assert versions[0].version_no == 1
    assert versions[0].metadata_snapshot["title"] == "First published title"
    assert versions[0].metadata_snapshot["version_no"] == 1
    assert versions[0].change_reason == "Approve initial version"


@pytest.mark.anyio
async def test_approve_revision_creates_metadata_version_for_new_snapshot(sample_user, monkeypatch, no_log_side_effects):
    core_obj = _approved_core_record(title="Original title", version_no=1)
    staging_obj = _pending_staging_record(
        source_core_research_id=core_obj.research_id,
        title="Revised approved title",
        update_reason="Correct approved metadata",
    )
    _FakeCoreApproveRepository.staging_obj = staging_obj
    _FakeCoreApproveRepository.core_obj = core_obj
    monkeypatch.setattr(approve_service_module, "CoreApproveRepository", _FakeCoreApproveRepository)
    db = _ServiceFakeDbSession()

    await core_approve_service.approve_record(
        db,
        staging_id=staging_obj.staging_id,
        payload=ApproveRequest(note="Approve revision", access_level=AccessLevel.public),
        current_user=sample_user,
    )

    versions = [item for item in db.added if isinstance(item, CoreMetadataVersion)]
    assert len(versions) == 1
    assert core_obj.version_no == 2
    assert versions[0].version_no == 2
    assert versions[0].metadata_snapshot["title"] == "Revised approved title"
    assert versions[0].metadata_snapshot["version_no"] == 2
    assert versions[0].change_reason == "Correct approved metadata"


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
        return {
            "items": [
                {
                    "research_id": research_id,
                    "title": "PostgreSQL Search Benchmark",
                    "year": 2026,
                    "access_level": "public",
                    "version_no": 2,
                    "approved_at": "2026-05-26T00:00:00Z",
                    "rank": 0.75,
                }
            ],
            "total": 1,
            "limit": 20,
            "offset": 0,
        }

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(f"{settings.API_V1_PREFIX}/search/core?q=benchmark")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["research_id"] == str(research_id)


def test_postgres_search_strips_query_and_passes_pagination(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    captured = {}

    async def _fake_search(*args, **kwargs):
        captured.update(kwargs)
        return {"items": [], "total": 0, "limit": kwargs["limit"], "offset": kwargs["offset"]}

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(
        f"{settings.API_V1_PREFIX}/search/core",
        params={"q": "  trí tuệ  ", "limit": 5, "offset": 2},
    )

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 5, "offset": 2}
    assert captured["query"] == "trí tuệ"
    assert captured["limit"] == 5
    assert captured["offset"] == 2


def test_unauthenticated_user_can_search_core_records(client, monkeypatch):
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    async def _fake_search(*_args, **_kwargs):
        return {"items": [], "total": 0, "limit": 20, "offset": 0}

    monkeypatch.setattr(search_endpoint.search_service, "search_core_postgres", _fake_search)

    response = client.get(f"{settings.API_V1_PREFIX}/search/core?q=benchmark")

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


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

    response = await search_service.search_core_postgres(db, query="tri tue nhan tao", limit=10, offset=0)

    assert response.items == []
    assert response.total == 0
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
    assert "identifier" in compiled_sql
    assert compiled_sql.count(" ilike ") == 1
    assert "research_object_authors" not in compiled_sql
    assert "research_object_keywords" not in compiled_sql
    assert "research_object_domains" not in compiled_sql


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
