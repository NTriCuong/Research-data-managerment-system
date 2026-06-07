import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.database.session import get_db
from app.main import app
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.enum import UserStatus
from app.models.logs.audit_log import AuditLog
from app.services.auth.deps import get_current_active_user


def _require_test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run integration tests.")
    return url


@pytest_asyncio.fixture
async def srs_db_session():
    engine = create_async_engine(_require_test_db_url())
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture
async def super_admin(srs_db_session: AsyncSession):
    role = (
        await srs_db_session.execute(select(Role).where(Role.role_code == "SUPER_ADMIN"))
    ).scalar_one()
    suffix = uuid4().hex[:10]
    user = User(
        username=f"admin_{suffix}",
        email=f"admin_{suffix}@example.com",
        password_hash="hash",
        full_name="SRS Integration Admin",
        role_id=role.role_id,
        status=UserStatus.active,
        created_at=datetime.now(timezone.utc),
    )
    srs_db_session.add(user)
    await srs_db_session.commit()
    await srs_db_session.refresh(user)
    user.role = role

    try:
        yield user
    finally:
        await srs_db_session.rollback()
        await srs_db_session.execute(delete(AuditLog).where(AuditLog.actor_user_id == user.user_id))
        await srs_db_session.execute(delete(User).where(User.user_id == user.user_id))
        await srs_db_session.commit()


@pytest_asyncio.fixture
async def admin_api_client(srs_db_session: AsyncSession, super_admin: User):
    async def _override_get_db():
        try:
            yield srs_db_session
            await srs_db_session.commit()
        except Exception:
            await srs_db_session.rollback()
            raise

    async def _override_current_user():
        return super_admin

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_active_user] = _override_current_user
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client
    app.dependency_overrides = {}


@pytest.fixture
def api_prefix() -> str:
    return settings.API_V1_PREFIX
