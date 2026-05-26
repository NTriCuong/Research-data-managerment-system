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
from app.database.config import get_db
from app.main import app
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.enum import AccessLevel, UserStatus, WorkflowStatus
from app.models.reference.department import Department
from app.models.reference.output_type import OutputType
from app.models.staging.stg_file_attachment import StgFileAttachment
from app.models.staging.stg_research_object import StgResearchObject
from app.core import permissions
from app.models.logs.workflow_history import WorkflowHistory

pytestmark = pytest.mark.asyncio


def _require_test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run DB integration tests.")
    return url


@pytest_asyncio.fixture
async def db_session():
    test_db_url = _require_test_db_url()
    engine = create_async_engine(test_db_url, future=True)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


async def _seed_required_data(db: AsyncSession):

    dept_code = f"DEPT_{uuid4().hex[:8]}"
    type_code = f"TYPE_{uuid4().hex[:8]}"
    username = f"u_{uuid4().hex[:8]}"
    email = f"{uuid4().hex[:8]}@example.com"

    # lấy role có sẵn
    result = await db.execute(
        select(Role).where(Role.role_code == "DATA_ENTRY")
    )
    role = result.scalar_one_or_none()

    if role is None:
        raise RuntimeError(
            "Missing DATA_ENTRY role in test database"
        )

    dept = Department(
        department_code=dept_code,
        department_name="Department Test",
    )

    output_type = OutputType(
        type_code=type_code,
        type_name="Output Type Test",
    )

    db.add_all([dept, output_type])
    await db.flush()

    user = User(
        username=username,
        email=email,
        password_hash="hashed",
        full_name="Test User",
        role_id=role.role_id,
        department_id=dept.department_id,
        status=UserStatus.active,
        created_at=datetime.now(timezone.utc),
    )

    db.add(user)
    await db.flush()

    staging_obj = StgResearchObject(
        title="Integration upload test",
        output_type_id=output_type.output_type_id,
        department_id=dept.department_id,
        year=2026,
        workflow_status=WorkflowStatus.draft,
        access_level=AccessLevel.internal,
        created_by=user.user_id,
    )

    db.add(staging_obj)
    await db.commit()

    await db.refresh(user)
    await db.refresh(staging_obj)

    user.role = role

    return SimpleNamespace(
        user=user,
        role=role,
        department=dept,
        output_type=output_type,
        staging_obj=staging_obj,
        staging_id=staging_obj.staging_id,
        user_id=user.user_id,
        department_id=dept.department_id,
        output_type_id=output_type.output_type_id,
    )

async def _cleanup_seeded_data(
    db: AsyncSession,
    seeded
) -> None:

    staging_id = seeded.staging_id
    user_id = seeded.user_id
    department_id = seeded.department_id
    output_type_id = seeded.output_type_id

    # delete child tables first
    await db.execute(
        delete(WorkflowHistory).where(
            WorkflowHistory.staging_id == staging_id
        )
    )

    await db.execute(
        delete(StgFileAttachment).where(
            StgFileAttachment.staging_id == staging_id
        )
    )

    # then parent
    await db.execute(
        delete(StgResearchObject).where(
            StgResearchObject.staging_id == staging_id
        )
    )

    await db.execute(
        delete(User).where(
            User.user_id == user_id
        )
    )

    await db.execute(
        delete(Department).where(
            Department.department_id == department_id
        )
    )

    await db.execute(
        delete(OutputType).where(
            OutputType.output_type_id == output_type_id
        )
    )

    await db.commit()


@pytest_asyncio.fixture
async def seeded_context(db_session: AsyncSession):
    seeded = await _seed_required_data(db_session)
    try:
        yield seeded
    finally:
        await _cleanup_seeded_data(db_session, seeded)


@pytest_asyncio.fixture
async def api_client(db_session: AsyncSession, seeded_context):
    async def _override_get_db():
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
            raise

    async def _override_current_user():
        return seeded_context.user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[permissions.get_current_active_user] = _override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides = {}


async def test_upload_endpoint_uses_real_test_db_and_mocked_r2(api_client: AsyncClient, db_session: AsyncSession, seeded_context, monkeypatch):
    monkeypatch.setattr(
        "app.services.storage.file_service.upload_bytes_to_r2",
        lambda **kwargs: SimpleNamespace(storage_path=kwargs["object_key"], public_url=None),
    )

    response = await api_client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata/{seeded_context.staging_id}/files",
        files={"file": ("evidence.pdf", b"test-pdf-content", "application/pdf")},
        data={"access_level": "internal"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["staging_id"] == str(seeded_context.staging_id)
    assert body["original_filename"] == "evidence.pdf"
    assert body["mime_type"] == "application/pdf"
    assert body["storage_path"].startswith(f"staging/{seeded_context.staging_id}/")

    result = await db_session.execute(select(StgFileAttachment).where(StgFileAttachment.file_id == body["file_id"]))
    saved_file = result.scalar_one_or_none()
    assert saved_file is not None
    assert saved_file.original_filename == "evidence.pdf"
    assert saved_file.file_size_bytes == len(b"test-pdf-content")


async def test_upload_endpoint_rejects_large_file_without_calling_r2(api_client: AsyncClient, seeded_context, monkeypatch):
    calls = {"count": 0}

    def _fake_upload(**_kwargs):
        calls["count"] += 1
        return SimpleNamespace(storage_path="x", public_url=None)

    monkeypatch.setattr("app.services.storage.file_service.upload_bytes_to_r2", _fake_upload)

    large_bytes = b"a" * (50 * 1024 * 1024 + 1)
    response = await api_client.post(
        f"{settings.API_V1_PREFIX}/staging-metadata/{seeded_context.staging_id}/files",
        files={"file": ("too-large.pdf", large_bytes, "application/pdf")},
        data={"access_level": "internal"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File size exceeds 50MB limit"
    assert calls["count"] == 0
