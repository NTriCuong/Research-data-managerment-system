from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs.audit_log import AuditLog


pytestmark = pytest.mark.asyncio


async def test_super_admin_can_manage_all_reference_data(
    admin_api_client: AsyncClient,
    srs_db_session: AsyncSession,
    super_admin,
    api_prefix: str,
):
    suffix = uuid4().hex[:10]
    cases = [
        {
            "collection": "departments",
            "item": "department",
            "id": "department_id",
            "create": {
                "department_code": f"DEPT_{suffix}",
                "department_name": "Reference Department",
            },
            "update": {"department_name": "Updated Department"},
            "field": "department_name",
            "updated": "Updated Department",
        },
        {
            "collection": "output-types/",
            "item": "output-types",
            "id": "output_type_id",
            "create": {
                "type_code": f"TYPE_{suffix}",
                "type_name": "Reference Output Type",
            },
            "update": {"type_name": "Updated Output Type"},
            "field": "type_name",
            "updated": "Updated Output Type",
        },
        {
            "collection": "research-domains/",
            "item": "research-domains",
            "id": "domain_id",
            "create": {
                "domain_code": f"DOMAIN_{suffix}",
                "domain_name": "Reference Domain",
            },
            "update": {"domain_name": "Updated Domain"},
            "field": "domain_name",
            "updated": "Updated Domain",
        },
        {
            "collection": "researchers/",
            "item": "researchers",
            "id": "researcher_id",
            "create": {
                "full_name": "Reference Researcher",
                "email": f"researcher_{suffix}@example.com",
                "researcher_code": f"RES_{suffix}",
            },
            "update": {"full_name": "Updated Researcher"},
            "field": "full_name",
            "updated": "Updated Researcher",
        },
        {
            "collection": "keywords/",
            "item": "keywords",
            "id": "keyword_id",
            "create": {
                "keyword_text": f"reference-keyword-{suffix}",
                "normalized_text": f"reference keyword {suffix}",
            },
            "update": {"normalized_text": f"updated keyword {suffix}"},
            "field": "normalized_text",
            "updated": f"updated keyword {suffix}",
        },
    ]

    for case in cases:
        create_path = f"{api_prefix}/reference/{case['item']}"
        if case["item"] != "department":
            create_path += "/"
        create_response = await admin_api_client.post(create_path, json=case["create"])
        assert create_response.status_code == 201, create_response.text
        item_id = create_response.json()[case["id"]]

        get_response = await admin_api_client.get(
            f"{api_prefix}/reference/{case['item']}/{item_id}"
        )
        assert get_response.status_code == 200

        update_response = await admin_api_client.put(
            f"{api_prefix}/reference/{case['item']}/{item_id}",
            json=case["update"],
        )
        assert update_response.status_code == 200, update_response.text
        assert update_response.json()[case["field"]] == case["updated"]

        list_response = await admin_api_client.get(
            f"{api_prefix}/reference/{case['collection']}"
        )
        assert list_response.status_code == 200
        assert any(row[case["id"]] == item_id for row in list_response.json())

        delete_response = await admin_api_client.delete(
            f"{api_prefix}/reference/{case['item']}/{item_id}"
        )
        assert delete_response.status_code == 204, delete_response.text

    audit_actions = set(
        (
            await srs_db_session.execute(
                select(AuditLog.action_code).where(
                    AuditLog.actor_user_id == super_admin.user_id
                )
            )
        ).scalars()
    )
    assert {
        "CREATE_DEPARTMENT",
        "CREATE_OUTPUT_TYPE",
        "CREATE_RESEARCH_DOMAIN",
        "CREATE_RESEARCHER",
        "CREATE_KEYWORD",
    } <= audit_actions

    await srs_db_session.execute(delete(AuditLog).where(AuditLog.actor_user_id == super_admin.user_id))
    await srs_db_session.commit()
