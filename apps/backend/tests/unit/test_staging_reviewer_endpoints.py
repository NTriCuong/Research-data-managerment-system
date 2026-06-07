from types import SimpleNamespace
from uuid import uuid4

from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps
from app.api.v1.endpoints import staging_review as staging_endpoint


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


def test_reviewer_can_list_pending_records(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_list_pending(*_args, **_kwargs):
        return [
            {
                "staging_id": staging_id,
                "title": "Pending Record",
                "output_type_id": uuid4(),
                "department_id": uuid4(),
                "year": 2026,
                "workflow_status": "pending_review",
                "access_level": "internal",
                "source_core_research_id": None,
                "update_reason": None,
                "metadata_quality_score": None,
                "created_by": sample_user.user_id,
                "submitted_by": sample_user.user_id,
                "submitted_at": None,
                "created_at": "2026-05-26T00:00:00Z",
                "updated_at": None,
            }
        ]

    monkeypatch.setattr(staging_endpoint.staging_review_service, "list_pending_review_records", _fake_list_pending)

    response = client.get(f"{settings.API_V1_PREFIX}/staging-review/pending")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["staging_id"] == str(staging_id)
    assert body[0]["workflow_status"] == "pending_review"


def test_reviewer_pending_list_passes_pagination(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    captured = {}

    async def _fake_list_pending(*_args, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(staging_endpoint.staging_review_service, "list_pending_review_records", _fake_list_pending)

    response = client.get(
        f"{settings.API_V1_PREFIX}/staging-review/pending",
        params={"limit": 6, "offset": 2},
    )

    assert response.status_code == 200
    assert response.json() == []
    assert captured["limit"] == 6
    assert captured["offset"] == 2


def test_reviewer_can_request_revision(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_request_revision(*_args, **_kwargs):
        return {"message": "Revision requested"}

    monkeypatch.setattr(staging_endpoint.staging_review_service, "request_revision", _fake_request_revision)

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-review/{staging_id}/request-revision",
        json={"note": "Missing author affiliation"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Revision requested"


def test_request_revision_requires_note(client, sample_user):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-review/{uuid4()}/request-revision",
        json={"note": ""},
    )

    assert response.status_code == 422


def test_reviewer_can_forward_to_approval(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    async def _fake_forward(*_args, **_kwargs):
        return {"message": "Forwarded to approval"}

    monkeypatch.setattr(staging_endpoint.staging_review_service, "forward_to_approval", _fake_forward)

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-review/{staging_id}/forward",
        json={"note": "Metadata is complete"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Forwarded to approval"


def test_data_entry_cannot_use_reviewer_actions(client, sample_user):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    staging_id = uuid4()

    response = client.post(
        f"{settings.API_V1_PREFIX}/staging-review/{staging_id}/forward",
        json={"note": "Try bypass role"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Bạn không có đủ quyền để thực hiện thao tác này"
