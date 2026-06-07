from types import SimpleNamespace
from uuid import uuid4

from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps
from app.api.v1.endpoints import auth as auth_endpoint
from app.core.exceptions import UnauthorizedException


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


def _prepare_token_user(user):
    user.role.role_name = getattr(user.role, "role_name", "Super Admin")
    user.department = getattr(user, "department", None)
    return user


def test_auth_login_success_sets_refresh_cookie(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        return "access-token", "refresh-token", _prepare_token_user(sample_user)

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"username": sample_user.username, "password": "Password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access-token"
    assert body["token_type"] == "bearer"
    assert body["user"]["user_id"] == str(sample_user.user_id)
    assert "refresh_token=" in response.headers.get("set-cookie", "")


def test_auth_token_form_login_success_sets_refresh_cookie(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        assert kwargs["username"] == sample_user.username
        assert kwargs["password"] == "Password123"
        return "form-access-token", "form-refresh-token", _prepare_token_user(sample_user)

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/token",
        data={"username": sample_user.username, "password": "Password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "form-access-token"
    assert body["user"]["username"] == sample_user.username
    assert "refresh_token=form-refresh-token" in response.headers.get("set-cookie", "")


def test_auth_refresh_success_rotates_cookie(client, sample_user, monkeypatch):
    db_token = SimpleNamespace(revoked_at=None)
    _prepare_token_user(sample_user)

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
    assert response.json()["message"] == "Đăng xuất thành công"
    assert "refresh_token=" in response.headers.get("set-cookie", "")


def test_auth_me_returns_current_user(client, sample_user, override_active_user):
    response = client.get(f"{settings.API_V1_PREFIX}/users/me")

    assert response.status_code == 200
    assert response.json()["user_id"] == str(sample_user.user_id)


def test_auth_login_rejects_missing_username(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        return "access-token", "refresh-token", _prepare_token_user(sample_user)

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"email": sample_user.email, "password": "Password123"},
    )

    assert response.status_code == 422


def test_auth_login_propagates_invalid_credentials(client, sample_user, monkeypatch):
    async def _fake_login(*args, **kwargs):
        raise UnauthorizedException("Thông tin đăng nhập không hợp lệ")

    monkeypatch.setattr(auth_endpoint.auth_service, "login", _fake_login)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/login",
        json={"username": sample_user.username, "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Thông tin đăng nhập không hợp lệ"


def test_auth_change_password_success(client, sample_user, monkeypatch, override_active_user):
    async def _fake_change_password(*args, **kwargs):
        return None

    monkeypatch.setattr(auth_endpoint.auth_service, "change_password", _fake_change_password)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/change-password",
        json={"current_password": "OldPass123", "new_password": "NewPass123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Đổi mật khẩu thành công"


def test_auth_admin_reset_password_requires_super_admin(client, sample_user, monkeypatch, override_active_user):
    sample_user.role = SimpleNamespace(role_code="REVIEWER")
    user_id = uuid4()

    async def _fake_reset(*args, **kwargs):
        return None

    monkeypatch.setattr(auth_endpoint.auth_service, "admin_reset_password", _fake_reset)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/admin/reset-password/{user_id}",
        json={"new_password": "ResetPass123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Bạn không có đủ quyền để thực hiện thao tác này"


def test_auth_admin_reset_password_success(client, sample_user, monkeypatch, override_active_user):
    sample_user.role = SimpleNamespace(role_code="SUPER_ADMIN")
    user_id = uuid4()

    async def _fake_reset(*args, **kwargs):
        return None

    monkeypatch.setattr(auth_endpoint.auth_service, "admin_reset_password", _fake_reset)
    client.app.dependency_overrides[get_db] = _fake_db_provider(sample_user)

    response = client.post(
        f"{settings.API_V1_PREFIX}/auth/admin/reset-password/{user_id}",
        json={"new_password": "ResetPass123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Đặt lại mật khẩu thành công"
