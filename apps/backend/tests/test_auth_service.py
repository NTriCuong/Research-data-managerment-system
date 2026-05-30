import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

import app.services.auth.auth_service as auth_service_module
from app.models.enum import UserStatus


class _FakeDb:
    pass


def _make_user(role_code: str = "SUPER_ADMIN"):
    return SimpleNamespace(
        user_id=uuid4(),
        username="user1",
        email="user1@example.com",
        password_hash="hashed-old",
        full_name="User One",
        role=SimpleNamespace(role_code=role_code),
        role_id=uuid4(),
        department_id=None,
        status=UserStatus.active,
        deleted_at=None,
        updated_at=None,
    )


def test_token_lifetime_policy_rejects_access_token_over_30(monkeypatch):
    monkeypatch.setattr(auth_service_module.settings, "ACCESS_TOKEN_EXPIRE", 31)
    monkeypatch.setattr(auth_service_module.settings, "REFRESH_TOKEN_EXPIRE", 7)

    with pytest.raises(HTTPException) as exc:
        auth_service_module.auth_service._validate_token_lifetime_policy()

    assert exc.value.status_code == 500
    assert "ACCESS_TOKEN_EXPIRE" in exc.value.detail


def test_token_lifetime_policy_rejects_refresh_token_over_7(monkeypatch):
    monkeypatch.setattr(auth_service_module.settings, "ACCESS_TOKEN_EXPIRE", 30)
    monkeypatch.setattr(auth_service_module.settings, "REFRESH_TOKEN_EXPIRE", 8)

    with pytest.raises(HTTPException) as exc:
        auth_service_module.auth_service._validate_token_lifetime_policy()

    assert exc.value.status_code == 500
    assert "REFRESH_TOKEN_EXPIRE" in exc.value.detail


def test_change_password_success_updates_hash_and_revokes_sessions(monkeypatch):
    user = _make_user()
    db = _FakeDb()

    monkeypatch.setattr(auth_service_module, "verify_password", lambda plain, hashed: True)
    monkeypatch.setattr(auth_service_module, "hash_password", lambda plain: "new-hash")

    called = {"revoked": False, "audit": False}

    async def _fake_revoke(*args, **kwargs):
        called["revoked"] = True
        return 1

    async def _fake_audit(*args, **kwargs):
        called["audit"] = True
        return None

    monkeypatch.setattr(auth_service_module.auth_service, "revoke_all_sessions", _fake_revoke)
    monkeypatch.setattr(auth_service_module.audit_service, "write_log", _fake_audit)

    asyncio.run(
        auth_service_module.auth_service.change_password(
            db,
            user=user,
            old_password="OldPass123",
            new_password="NewPass123",
        )
    )

    assert user.password_hash == "new-hash"
    assert isinstance(user.updated_at, datetime)
    assert called["revoked"] is True
    assert called["audit"] is True


def test_change_password_rejects_wrong_current_password(monkeypatch):
    user = _make_user()
    db = _FakeDb()

    monkeypatch.setattr(auth_service_module, "verify_password", lambda plain, hashed: False)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            auth_service_module.auth_service.change_password(
                db,
                user=user,
                old_password="WrongPass",
                new_password="NewPass123",
            )
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Current password is incorrect"


def test_admin_reset_password_not_found(monkeypatch):
    db = _FakeDb()
    actor = _make_user("SUPER_ADMIN")

    class _FakeRepo:
        def __init__(self, _db):
            self.db = _db

        async def find_user_by_id_with_role(self, user_id):
            return None

    monkeypatch.setattr(auth_service_module, "AuthRepository", _FakeRepo)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            auth_service_module.auth_service.admin_reset_password(
                db,
                actor=actor,
                user_id=uuid4(),
                new_password="ResetPass123",
            )
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


def test_admin_reset_password_success(monkeypatch):
    db = _FakeDb()
    actor = _make_user("SUPER_ADMIN")
    target_user = _make_user("DATA_ENTRY")

    class _FakeRepo:
        def __init__(self, _db):
            self.db = _db

        async def find_user_by_id_with_role(self, user_id):
            return target_user

    monkeypatch.setattr(auth_service_module, "AuthRepository", _FakeRepo)
    monkeypatch.setattr(auth_service_module, "hash_password", lambda plain: "reset-hash")

    called = {"revoked": False, "audit": False}

    async def _fake_revoke(*args, **kwargs):
        called["revoked"] = True
        return 1

    async def _fake_audit(*args, **kwargs):
        called["audit"] = True
        return None

    monkeypatch.setattr(auth_service_module.auth_service, "revoke_all_sessions", _fake_revoke)
    monkeypatch.setattr(auth_service_module.audit_service, "write_log", _fake_audit)

    asyncio.run(
        auth_service_module.auth_service.admin_reset_password(
            db,
            actor=actor,
            user_id=target_user.user_id,
            new_password="ResetPass123",
        )
    )

    assert target_user.password_hash == "reset-hash"
    assert isinstance(target_user.updated_at, datetime)
    assert target_user.updated_at.tzinfo is not None
    assert called["revoked"] is True
    assert called["audit"] is True
