from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.role import Role
from app.models.auth.user import User
from app.models.logs.audit_log import AuditLog


pytestmark = pytest.mark.asyncio


async def test_super_admin_can_manage_user_lifecycle(
    admin_api_client: AsyncClient,
    srs_db_session: AsyncSession,
    super_admin,
    api_prefix: str,
):
    suffix = uuid4().hex[:10]
    roles = {
        role.role_code: role.role_id
        for role in (
            await srs_db_session.execute(
                select(Role).where(Role.role_code.in_(["DATA_ENTRY", "REVIEWER"]))
            )
        ).scalars()
    }
    create_response = await admin_api_client.post(
        f"{api_prefix}/users",
        json={
            "username": f"managed_{suffix}",
            "email": f"managed_{suffix}@example.com",
            "password": "StrongPassword123!",
            "full_name": "Managed User",
            "role_id": str(roles["DATA_ENTRY"]),
        },
    )
    assert create_response.status_code == 201, create_response.text
    user_id = create_response.json()["user_id"]

    list_response = await admin_api_client.get(
        f"{api_prefix}/users",
        params={"q": f"managed_{suffix}"},
    )
    assert list_response.status_code == 200
    assert [row["user_id"] for row in list_response.json()] == [user_id]

    get_response = await admin_api_client.get(f"{api_prefix}/users/{user_id}")
    assert get_response.status_code == 200

    update_response = await admin_api_client.put(
        f"{api_prefix}/users/{user_id}",
        json={"full_name": "Managed User Updated"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["full_name"] == "Managed User Updated"

    status_response = await admin_api_client.put(
        f"{api_prefix}/users/{user_id}/status",
        json={"status": "disabled"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "disabled"

    role_response = await admin_api_client.put(
        f"{api_prefix}/users/{user_id}/role",
        json={"role_id": str(roles["REVIEWER"])},
    )
    assert role_response.status_code == 200
    assert role_response.json()["role_id"] == str(roles["REVIEWER"])

    delete_response = await admin_api_client.delete(f"{api_prefix}/users/{user_id}")
    assert delete_response.status_code == 200
    deleted_user = (
        await srs_db_session.execute(select(User).where(User.user_id == user_id))
    ).scalar_one()
    assert deleted_user.deleted_at is not None

    actions = set(
        (
            await srs_db_session.execute(
                select(AuditLog.action_code).where(AuditLog.target_id == user_id)
            )
        ).scalars()
    )
    assert {
        "ADMIN_CREATE_USER",
        "ADMIN_UPDATE_USER",
        "ADMIN_UPDATE_USER_STATUS",
        "ADMIN_ASSIGN_ROLE",
        "ADMIN_SOFT_DELETE_USER",
    } <= actions

    await srs_db_session.execute(delete(AuditLog).where(AuditLog.target_id == user_id))
    await srs_db_session.execute(delete(User).where(User.user_id == user_id))
    await srs_db_session.commit()
