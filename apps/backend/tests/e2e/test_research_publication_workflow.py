import os
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.database.session import get_db
from app.main import app
from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.core.core_metadata_version import CoreMetadataVersion
from app.models.core.core_research_object import CoreResearchObject
from app.models.enum import UserStatus
from app.models.reference.department import Department
from app.models.reference.keyword import Keyword
from app.models.reference.output_type import OutputType
from app.models.reference.research_domain import ResearchDomain
from app.models.reference.researcher import Researcher
from app.services.auth.deps import get_current_active_user


pytestmark = pytest.mark.asyncio


def _require_test_db_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run E2E tests.")
    return url


@pytest_asyncio.fixture
async def workflow_context():
    engine = create_async_engine(_require_test_db_url())
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        role = (
            await session.execute(select(Role).where(Role.role_code == "SUPER_ADMIN"))
        ).scalar_one()
        suffix = uuid4().hex[:10]
        department = Department(
            department_code=f"E2E_DEPT_{suffix}",
            department_name="E2E Department",
        )
        output_type = OutputType(
            type_code=f"E2E_TYPE_{suffix}",
            type_name="E2E Output Type",
        )
        domain = ResearchDomain(
            domain_code=f"E2E_DOMAIN_{suffix}",
            domain_name="E2E Research Domain",
        )
        keyword = Keyword(
            keyword_text=f"e2e-keyword-{suffix}",
            normalized_text=f"e2e keyword {suffix}",
        )
        researcher = Researcher(
            full_name="Nguyen Van Hai",
            email=f"researcher_{suffix}@example.com",
            researcher_code=f"E2E_RES_{suffix}",
            is_internal=True,
        )
        session.add_all([department, output_type, domain, keyword, researcher])
        await session.flush()
        user = User(
            username=f"e2e_admin_{suffix}",
            email=f"e2e_admin_{suffix}@example.com",
            password_hash="hash",
            full_name="E2E Super Admin",
            role_id=role.role_id,
            status=UserStatus.active,
            created_at=datetime.now(timezone.utc),
        )
        session.add(user)
        await session.flush()
        user.role = role

        async def _override_get_db():
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

        async def _override_current_user():
            return user

        app.dependency_overrides[get_db] = _override_get_db
        app.dependency_overrides[get_current_active_user] = _override_current_user
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield SimpleNamespace(
                client=client,
                session=session,
                user=user,
                department=department,
                output_type=output_type,
                domain=domain,
                keyword=keyword,
                researcher=researcher,
                suffix=suffix,
            )

        app.dependency_overrides = {}
        await session.close()
        await transaction.rollback()
    await engine.dispose()


async def test_full_publication_and_approved_revision_workflow(workflow_context, monkeypatch):
    context = workflow_context
    client = context.client
    prefix = settings.API_V1_PREFIX
    original_title = f"Nghiên cứu dữ liệu biển {context.suffix}"
    revised_title = f"Nghiên cứu dữ liệu biển cập nhật {context.suffix}"

    monkeypatch.setattr(
        "app.services.storage.file_service.upload_fileobj_to_r2",
        lambda **kwargs: SimpleNamespace(
            storage_path=kwargs["object_key"],
            public_url=None,
        ),
    )

    create_response = await client.post(
        f"{prefix}/staging-metadata",
        json={
            "title": original_title,
            "description": "E2E publication workflow",
            "abstract": "End-to-end research metadata",
            "output_type_id": str(context.output_type.output_type_id),
            "department_id": str(context.department.department_id),
            "year": 2026,
            "domain_ids": [str(context.domain.domain_id)],
            "keyword_ids": [str(context.keyword.keyword_id)],
            "authors": [
                {
                    "researcher_id": str(context.researcher.researcher_id),
                    "author_order": 1,
                }
            ],
        },
    )
    assert create_response.status_code == 201, create_response.text
    staging_id = create_response.json()["staging_id"]

    upload_response = await client.post(
        f"{prefix}/staging-metadata/{staging_id}/files",
        files={"file": ("e2e-evidence.pdf", b"e2e-pdf-content", "application/pdf")},
    )
    assert upload_response.status_code == 201, upload_response.text
    file_id = upload_response.json()["file_id"]

    submit_response = await client.post(
        f"{prefix}/staging-metadata/{staging_id}/submit",
        json={"note": "Ready for review"},
    )
    assert submit_response.status_code == 200, submit_response.text

    forward_response = await client.post(
        f"{prefix}/staging-review/{staging_id}/forward",
        json={"note": "Metadata reviewed"},
    )
    assert forward_response.status_code == 200, forward_response.text

    approve_response = await client.post(
        f"{prefix}/core-approve/{staging_id}/approve",
        json={
            "note": "Approved for publication",
            "access_level": "public",
            "file_access_levels": [{"file_id": file_id, "access_level": "public"}],
        },
    )
    assert approve_response.status_code == 200, approve_response.text

    core_record = (
        await context.session.execute(
            select(CoreResearchObject).where(
                CoreResearchObject.source_staging_id == staging_id
            )
        )
    ).scalar_one()
    research_id = str(core_record.research_id)
    assert core_record.title == original_title
    assert core_record.version_no == 1

    search_response = await client.get(
        f"{prefix}/search/core",
        params={"q": f"du lieu bien {context.suffix}"},
    )
    assert search_response.status_code == 200
    assert search_response.json()["total"] >= 1
    assert any(row["research_id"] == research_id for row in search_response.json()["items"])

    for query in ("Nguyen Van Hai", context.keyword.keyword_text, context.domain.domain_name):
        fts_response = await client.get(f"{prefix}/search/core", params={"q": query})
        assert fts_response.status_code == 200
        assert any(row["research_id"] == research_id for row in fts_response.json()["items"])

    workflow_response = await client.get(
        f"{prefix}/logs/workflow",
        params={"staging_id": staging_id},
    )
    assert workflow_response.status_code == 200
    assert {
        "CREATE_DRAFT",
        "SUBMIT_FOR_REVIEW",
        "FORWARD_TO_APPROVAL",
        "APPROVE_RECORD",
    } <= {row["action_code"] for row in workflow_response.json()}

    audit_response = await client.get(
        f"{prefix}/logs/audit",
        params={"target_table": "research_objects"},
    )
    assert audit_response.status_code == 200
    assert any(
        row["action_code"] == "APPROVE_RECORD" and row["target_id"] == staging_id
        for row in audit_response.json()
    )

    revision_response = await client.post(
        f"{prefix}/staging-metadata/revisions",
        json={
            "research_id": research_id,
            "update_reason": "Correct the approved title",
        },
    )
    assert revision_response.status_code == 201, revision_response.text
    revision_id = revision_response.json()["staging_id"]
    assert revision_response.json()["source_core_research_id"] == research_id

    update_response = await client.put(
        f"{prefix}/staging-metadata/{revision_id}",
        json={"title": revised_title},
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["title"] == revised_title

    for path, payload in [
        (f"{prefix}/staging-metadata/{revision_id}/submit", {"note": "Submit revision"}),
        (f"{prefix}/staging-review/{revision_id}/forward", {"note": "Review revision"}),
        (
            f"{prefix}/core-approve/{revision_id}/approve",
            {"note": "Approve revision", "access_level": "public"},
        ),
    ]:
        response = await client.post(path, json=payload)
        assert response.status_code == 200, response.text

    context.session.expire_all()
    updated_core = (
        await context.session.execute(
            select(CoreResearchObject).where(CoreResearchObject.research_id == research_id)
        )
    ).scalar_one()
    versions = (
        await context.session.execute(
            select(CoreMetadataVersion).where(
                CoreMetadataVersion.research_id == research_id
            )
        )
    ).scalars().all()
    assert str(updated_core.research_id) == research_id
    assert updated_core.title == revised_title
    assert updated_core.version_no == 2
    versions_by_number = {version.version_no: version for version in versions}
    assert set(versions_by_number) == {1, 2}
    assert versions_by_number[1].metadata_snapshot["title"] == original_title
    assert versions_by_number[2].metadata_snapshot["title"] == revised_title

    revised_search_response = await client.get(
        f"{prefix}/search/core",
        params={"q": f"cap nhat {context.suffix}"},
    )
    assert revised_search_response.status_code == 200
    assert any(
        row["research_id"] == research_id and row["version_no"] == 2
        for row in revised_search_response.json()["items"]
    )
