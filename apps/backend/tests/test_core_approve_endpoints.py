from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints import core_approve as approve_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps


class _FakeDbSession:
    async def commit(self):
        return None


def _fake_db_provider():
    async def _override_get_db():
        yield _FakeDbSession()

    return _override_get_db


def _override_user_with_role(client, sample_user, role_code: str):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user


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

    async def _fake_approve(*_args, **_kwargs):
        return {"message": "Record approved and published to core"}

    monkeypatch.setattr(approve_endpoint.core_approve_service, "approve_record", _fake_approve)

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/approve",
        json={"note": "Approved for publication"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Record approved and published to core"


def test_approver_can_reject_record(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "APPROVER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_reject(*_args, **_kwargs):
        return {"message": "Record rejected"}

    monkeypatch.setattr(approve_endpoint.core_approve_service, "reject_record", _fake_reject)

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/reject",
        json={"reason": "Insufficient evidence"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Record rejected"


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
                "access_level": "internal",
                "version_no": 2,
                "approved_at": "2026-05-26T00:00:00Z",
                "rank": 0.75,
            }
        ]

    monkeypatch.setattr(approve_endpoint.core_approve_service, "search_core_postgres", _fake_search)

    response = client.get(f"{settings.API_V1_PREFIX}/core-approve/search?q=benchmark")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["research_id"] == str(research_id)


def test_data_entry_cannot_approve(client, sample_user):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    response = client.post(
        f"{settings.API_V1_PREFIX}/core-approve/{staging_id}/approve",
        json={"note": "Should fail"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
