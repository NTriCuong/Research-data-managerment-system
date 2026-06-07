import os
from uuid import uuid4

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine


pytestmark = pytest.mark.asyncio


def _test_database_url() -> str:
    load_dotenv()
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL database tests.")
    return url


@pytest_asyncio.fixture
async def db_connection():
    engine = create_async_engine(_test_database_url())
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()
    await engine.dispose()


async def _seed_required_records(connection):
    suffix = uuid4().hex[:10]
    role_id = await connection.scalar(
        text("SELECT role_id FROM auth.roles WHERE role_code = 'SUPER_ADMIN'")
    )
    assert role_id is not None, "Test database must be migrated and seeded with roles."

    department_id = await connection.scalar(
        text(
            """
            INSERT INTO reference.departments (department_code, department_name)
            VALUES (:code, 'SRS database test department')
            RETURNING department_id
            """
        ),
        {"code": f"SRS_DEPT_{suffix}"},
    )
    output_type_id = await connection.scalar(
        text(
            """
            INSERT INTO reference.output_types (type_code, type_name)
            VALUES (:code, 'SRS database test output type')
            RETURNING output_type_id
            """
        ),
        {"code": f"SRS_TYPE_{suffix}"},
    )
    user_id = await connection.scalar(
        text(
            """
            INSERT INTO auth.users (username, email, password_hash, full_name, role_id)
            VALUES (:username, :email, 'hash', 'SRS database tester', :role_id)
            RETURNING user_id
            """
        ),
        {
            "username": f"srs_{suffix}",
            "email": f"srs_{suffix}@example.com",
            "role_id": role_id,
        },
    )
    return {
        "department_id": department_id,
        "output_type_id": output_type_id,
        "role_id": role_id,
        "user_id": user_id,
    }


async def test_quality_score_does_not_award_points_when_year_is_null(db_connection):
    seeded = await _seed_required_records(db_connection)
    common = {
        "department_id": seeded["department_id"],
        "output_type_id": seeded["output_type_id"],
        "user_id": seeded["user_id"],
    }
    null_year_id = await db_connection.scalar(
        text(
            """
            INSERT INTO staging.research_objects
                (title, output_type_id, department_id, created_by, year)
            VALUES ('Quality without year', :output_type_id, :department_id, :user_id, NULL)
            RETURNING staging_id
            """
        ),
        common,
    )
    valid_year_id = await db_connection.scalar(
        text(
            """
            INSERT INTO staging.research_objects
                (title, output_type_id, department_id, created_by, year)
            VALUES ('Quality with year', :output_type_id, :department_id, :user_id, 2026)
            RETURNING staging_id
            """
        ),
        common,
    )

    null_quality = await db_connection.scalar(
        text("SELECT app.compute_staging_metadata_quality(:id)"),
        {"id": null_year_id},
    )
    valid_quality = await db_connection.scalar(
        text("SELECT app.compute_staging_metadata_quality(:id)"),
        {"id": valid_year_id},
    )

    assert null_quality["year_valid"] is False
    assert float(valid_quality["total"]) - float(null_quality["total"]) == 14


async def test_soft_deleted_user_allows_reusing_username_and_email(db_connection):
    seeded = await _seed_required_records(db_connection)
    suffix = uuid4().hex[:10]
    values = {
        "username": f"reuse_{suffix}",
        "email": f"reuse_{suffix}@example.com",
        "role_id": seeded["role_id"],
    }
    first_user_id = await db_connection.scalar(
        text(
            """
            INSERT INTO auth.users (username, email, password_hash, full_name, role_id)
            VALUES (:username, :email, 'hash', 'First user', :role_id)
            RETURNING user_id
            """
        ),
        values,
    )
    await db_connection.execute(
        text("UPDATE auth.users SET deleted_at = now() WHERE user_id = :id"),
        {"id": first_user_id},
    )
    second_user_id = await db_connection.scalar(
        text(
            """
            INSERT INTO auth.users (username, email, password_hash, full_name, role_id)
            VALUES (:username, :email, 'hash', 'Replacement user', :role_id)
            RETURNING user_id
            """
        ),
        values,
    )

    assert second_user_id != first_user_id


async def test_workflow_history_cannot_be_orphaned(db_connection):
    seeded = await _seed_required_records(db_connection)

    with pytest.raises(IntegrityError):
        async with db_connection.begin_nested():
            await db_connection.execute(
                text(
                    """
                    INSERT INTO log.workflow_history
                        (to_status, action_code, performed_by)
                    VALUES ('draft', 'ORPHAN_EVENT', :user_id)
                    """
                ),
                {"user_id": seeded["user_id"]},
            )


async def test_core_identifier_is_unique_only_for_active_records(db_connection):
    seeded = await _seed_required_records(db_connection)
    identifier = f"SRS-ID-{uuid4().hex[:10]}"
    values = {
        **seeded,
        "identifier": identifier,
    }
    first_id = await db_connection.scalar(
        text(
            """
            INSERT INTO core.research_objects
                (title, output_type_id, department_id, identifier, approved_by)
            VALUES ('First active record', :output_type_id, :department_id, :identifier, :user_id)
            RETURNING research_id
            """
        ),
        values,
    )

    with pytest.raises(IntegrityError):
        async with db_connection.begin_nested():
            await db_connection.execute(
                text(
                    """
                    INSERT INTO core.research_objects
                        (title, output_type_id, department_id, identifier, approved_by)
                    VALUES ('Duplicate active record', :output_type_id, :department_id, upper(:identifier), :user_id)
                    """
                ),
                values,
            )

    await db_connection.execute(
        text("UPDATE core.research_objects SET deleted_at = now() WHERE research_id = :id"),
        {"id": first_id},
    )
    replacement_id = await db_connection.scalar(
        text(
            """
            INSERT INTO core.research_objects
                (title, output_type_id, department_id, identifier, approved_by)
            VALUES ('Replacement active record', :output_type_id, :department_id, :identifier, :user_id)
            RETURNING research_id
            """
        ),
        values,
    )
    assert replacement_id != first_id


async def test_fts_indexes_author_keyword_and_vietnamese_with_or_without_accents(db_connection):
    seeded = await _seed_required_records(db_connection)
    suffix = uuid4().hex[:10]
    research_id = await db_connection.scalar(
        text(
            """
            INSERT INTO core.research_objects
                (title, output_type_id, department_id, approved_by)
            VALUES ('Nghiên cứu dữ liệu biển', :output_type_id, :department_id, :user_id)
            RETURNING research_id
            """
        ),
        seeded,
    )
    keyword_id = await db_connection.scalar(
        text(
            """
            INSERT INTO reference.keywords (keyword_text, normalized_text)
            VALUES (:keyword, :keyword)
            RETURNING keyword_id
            """
        ),
        {"keyword": f"tri tue nhan tao {suffix}"},
    )
    await db_connection.execute(
        text(
            """
            INSERT INTO core.research_object_authors (research_id, full_name)
            VALUES (:research_id, 'Nguyễn Văn Hải')
            """
        ),
        {"research_id": research_id},
    )
    await db_connection.execute(
        text(
            """
            INSERT INTO core.research_object_keywords (research_id, keyword_id)
            VALUES (:research_id, :keyword_id)
            """
        ),
        {"research_id": research_id, "keyword_id": keyword_id},
    )

    async def matches(query: str) -> bool:
        return bool(
            await db_connection.scalar(
                text(
                    """
                    SELECT search_vector @@ websearch_to_tsquery('simple', unaccent(:query))
                    FROM core.research_objects
                    WHERE research_id = :research_id
                    """
                ),
                {"query": query, "research_id": research_id},
            )
        )

    assert await matches("Nguyen Van Hai")
    assert await matches(f"tri tue nhan tao {suffix}")
    assert await matches("dữ liệu biển")
    assert await matches("du lieu bien")
