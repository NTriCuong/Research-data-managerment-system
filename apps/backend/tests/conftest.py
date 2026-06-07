import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

# Ensure env values parsed safely by pydantic-settings during app import.
os.environ["CORS_ORIGINS"] = '["http://localhost:3000"]'
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DEBUG"] = "false"

from app.main import app  # noqa: E402
from app.services.auth import deps as auth_deps  # noqa: E402


class DummyRole:
    def __init__(self, role_code: str = "SUPER_ADMIN") -> None:
        self.role_code = role_code


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides = {}
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


@pytest.fixture
def sample_user():
    return SimpleNamespace(
        user_id=uuid4(),
        username="admin",
        email="admin@example.com",
        password_hash="hashed",
        full_name="Admin User",
        role_id=uuid4(),
        department_id=None,
        status="active",
        last_login_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        deleted_at=None,
        role=DummyRole("SUPER_ADMIN"),
    )


@pytest.fixture
def override_active_user(sample_user):
    async def _override_current_active_user():
        return sample_user

    app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user
