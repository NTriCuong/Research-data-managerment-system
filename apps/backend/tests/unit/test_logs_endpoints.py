from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints import logs as logs_endpoint
from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps


class FakeDbSession:
    pass


def _fake_db_provider():
    async def _override_get_db():
        yield FakeDbSession()

    return _override_get_db


def _override_user_with_role(client, sample_user, role_code: str):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user


def test_super_admin_can_list_audit_logs_with_filters(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "SUPER_ADMIN")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    captured = {}
    audit_id = uuid4()

    async def _fake_list(*_args, **kwargs):
        captured.update(kwargs)
        return [
            {
                "audit_id": audit_id,
                "actor_user_id": sample_user.user_id,
                "action_code": "ADMIN_CREATE_USER",
                "target_schema": "auth",
                "target_table": "users",
                "target_id": uuid4(),
                "old_value": None,
                "new_value": {"username": "new-user"},
                "result": "success",
                "message": "created",
                "ip_address": "127.0.0.1",
                "user_agent": "pytest",
                "created_at": datetime.now(timezone.utc),
            }
        ]

    monkeypatch.setattr(logs_endpoint.log_query_service, "list_audit_logs", _fake_list)

    response = client.get(
        f"{settings.API_V1_PREFIX}/logs/audit",
        params={"action_code": "ADMIN_CREATE_USER", "target_table": "users", "limit": 10, "offset": 2},
    )

    assert response.status_code == 200
    assert response.json()[0]["audit_id"] == str(audit_id)
    assert captured["action_code"] == "ADMIN_CREATE_USER"
    assert captured["target_table"] == "users"
    assert captured["limit"] == 10
    assert captured["offset"] == 2


def test_super_admin_can_list_login_logs(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "SUPER_ADMIN")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    login_log_id = uuid4()

    async def _fake_list(*_args, **_kwargs):
        return [
            {
                "login_log_id": login_log_id,
                "user_id": sample_user.user_id,
                "username_attempted": sample_user.username,
                "login_result": "success",
                "failure_reason": None,
                "ip_address": "127.0.0.1",
                "user_agent": "pytest",
                "created_at": datetime.now(timezone.utc),
            }
        ]

    monkeypatch.setattr(logs_endpoint.log_query_service, "list_login_logs", _fake_list)

    response = client.get(f"{settings.API_V1_PREFIX}/logs/login")

    assert response.status_code == 200
    assert response.json()[0]["login_log_id"] == str(login_log_id)


def test_manager_can_list_workflow_logs(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "MANAGER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()
    workflow_id = uuid4()

    async def _fake_list(*_args, **_kwargs):
        return [
            {
                "workflow_id": workflow_id,
                "staging_id": uuid4(),
                "research_id": None,
                "from_status": "draft",
                "to_status": "pending_review",
                "action_code": "SUBMIT_FOR_REVIEW",
                "action_note": None,
                "performed_by": sample_user.user_id,
                "performed_at": datetime.now(timezone.utc),
                "ip_address": None,
                "user_agent": None,
            }
        ]

    monkeypatch.setattr(logs_endpoint.log_query_service, "list_workflow_logs", _fake_list)

    response = client.get(f"{settings.API_V1_PREFIX}/logs/workflow")

    assert response.status_code == 200
    assert response.json()[0]["workflow_id"] == str(workflow_id)


def test_manager_cannot_list_login_logs(client, sample_user):
    _override_user_with_role(client, sample_user, "MANAGER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    response = client.get(f"{settings.API_V1_PREFIX}/logs/login")

    assert response.status_code == 403
