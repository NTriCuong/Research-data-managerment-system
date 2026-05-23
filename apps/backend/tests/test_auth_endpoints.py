from types import SimpleNamespace
from uuid import uuid4

from app.core.config import settings
from app.database.config import get_db
from app.services.auth import deps as auth_deps
from app.api.v1.endpoints import auth as auth_endpoint


class _ExecuteResult:
    def __init__(self, user):
        self._user = user

    def scalar_one_or_none(self):
        return self._user


class _FakeSession:
    def __init__(self, user):
        self._user = user

    async def execute(self, _query):
        return _ExecuteResult(self._user)


def _fake_db_provider(user):
    async def _override_get_db():
        yield _FakeSession(user)

    return _override_get_db


def test_auth_login_success_sets_refresh_cookie(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        return "access-token", "refresh-token"

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    monkeypatch.setattr(auth_endpoint, "decode_access_token", lambda _token: {"sub": str(sample_user.user_id)})
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": sample_user.email, "password": "Password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access-token"
    assert body["token_type"] == "bearer"
    assert body["user"]["user_id"] == str(sample_user.user_id)
    assert "refresh_token=" in response.headers.get("set-cookie", "")


def test_auth_refresh_success_rotates_cookie(client, sample_user, monkeypatch):
    db_token = SimpleNamespace(revoked_at=None)

    async def _override_valid_refresh_token():
        return db_token, sample_user

    async def _fake_refresh_token(*args, **kwargs):
        return "new-access", "new-refresh"

    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)
    client.app.dependency_overrides[auth_deps.get_valid_refresh_token] = _override_valid_refresh_token
    monkeypatch.setattr(auth_endpoint.auth_service, "refresh_token", _fake_refresh_token)

    response = client.post(f"{settings.API_V1_PREFIX}/auth/refresh")

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "new-access"
    assert body["user"]["user_id"] == str(sample_user.user_id)
    assert "refresh_token=new-refresh" in response.headers.get("set-cookie", "")


def test_auth_logout_success_clears_cookie(client, sample_user, monkeypatch):
    db_token = SimpleNamespace(revoked_at=None)

    async def _override_valid_refresh_token():
        return db_token, sample_user

    async def _fake_logout(*args, **kwargs):
        return None

    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)
    client.app.dependency_overrides[auth_deps.get_valid_refresh_token] = _override_valid_refresh_token
    monkeypatch.setattr(auth_endpoint.auth_service, "logout", _fake_logout)

    response = client.post(f"{settings.API_V1_PREFIX}/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"
    assert "refresh_token=" in response.headers.get("set-cookie", "")


def test_auth_me_returns_current_user(client, sample_user, override_active_user):
    response = client.get(f"{settings.API_V1_PREFIX}/auth/me")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(sample_user.user_id)


def test_auth_login_500_when_token_missing_sub(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        return "access-token", "refresh-token"

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    monkeypatch.setattr(auth_endpoint, "decode_access_token", lambda _token: {})
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": sample_user.email, "password": "Password123"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Token missing subject"
