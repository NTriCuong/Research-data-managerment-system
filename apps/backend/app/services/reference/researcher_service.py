from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.researcher import Researcher
from app.services.logs.audit_service import audit_service


class ResearcherService:
    async def list_researchers(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Researcher], int]:
        offset = (page - 1) * page_size
        total = (await db.execute(select(func.count()).select_from(Researcher))).scalar_one()
        result = await db.execute(
            select(Researcher).order_by(Researcher.full_name.asc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_researcher(self, db: AsyncSession, *, researcher_id: UUID) -> Researcher | None:
        result = await db.execute(select(Researcher).where(Researcher.researcher_id == researcher_id))
        return result.scalar_one_or_none()

    async def get_researcher_by_email(self, db: AsyncSession, *, email: str) -> Researcher | None:
        result = await db.execute(select(Researcher).where(Researcher.email == email))
        return result.scalar_one_or_none()

    async def create_researcher(
        self,
        db: AsyncSession,
        *,
        full_name: str,
        email: str | None,
        orcid: str | None,
        department_id: UUID | None,
        academic_title: str | None,
        researcher_code: str | None,
        is_internal: bool,
        actor_user_id: UUID,
    ) -> Researcher:
        if email is not None and await self.get_researcher_by_email(db, email=email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

        researcher = Researcher(
            full_name=full_name,
            email=email,
            orcid=orcid,
            department_id=department_id,
            academic_title=academic_title,
            researcher_code=researcher_code,
            is_internal=is_internal,
        )
        db.add(researcher)
        await db.flush()
        await db.refresh(researcher)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="CREATE_RESEARCHER",
            target_schema="reference",
            target_table="researchers",
            target_id=researcher.researcher_id,
            new_value={
                "full_name": researcher.full_name,
                "email": researcher.email,
                "orcid": researcher.orcid,
                "department_id": str(researcher.department_id) if researcher.department_id else None,
                "academic_title": researcher.academic_title,
                "researcher_code": researcher.researcher_code,
                "is_internal": researcher.is_internal,
            },
            message="Created researcher",
        )

        return researcher

    async def update_researcher(
        self,
        db: AsyncSession,
        *,
        researcher_id: UUID,
        actor_user_id: UUID,
        full_name: str | None,
        email: str | None,
        orcid: str | None,
        department_id: UUID | None,
        academic_title: str | None,
        researcher_code: str | None,
        is_internal: bool | None,
        fields_set: set[str],
    ) -> Researcher | None:
        researcher = await self.get_researcher(db, researcher_id=researcher_id)
        if researcher is None:
            return None

        old_value = {
            "full_name": researcher.full_name,
            "email": researcher.email,
            "orcid": researcher.orcid,
            "department_id": str(researcher.department_id) if researcher.department_id else None,
            "academic_title": researcher.academic_title,
            "researcher_code": researcher.researcher_code,
            "is_internal": researcher.is_internal,
        }

        if "full_name" in fields_set:
            if full_name is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="full_name cannot be null")
            researcher.full_name = full_name

        if "email" in fields_set:
            if email is not None:
                existing = await self.get_researcher_by_email(db, email=email)
                if existing and existing.researcher_id != researcher_id:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
            researcher.email = email

        if "orcid" in fields_set:
            researcher.orcid = orcid
        if "department_id" in fields_set:
            researcher.department_id = department_id
        if "academic_title" in fields_set:
            researcher.academic_title = academic_title
        if "researcher_code" in fields_set:
            researcher.researcher_code = researcher_code
        if "is_internal" in fields_set:
            researcher.is_internal = bool(is_internal)

        researcher.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(researcher)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="UPDATE_RESEARCHER",
            target_schema="reference",
            target_table="researchers",
            target_id=researcher.researcher_id,
            old_value=old_value,
            new_value={
                "full_name": researcher.full_name,
                "email": researcher.email,
                "orcid": researcher.orcid,
                "department_id": str(researcher.department_id) if researcher.department_id else None,
                "academic_title": researcher.academic_title,
                "researcher_code": researcher.researcher_code,
                "is_internal": researcher.is_internal,
            },
            message="Updated researcher",
        )

        return researcher

    async def delete_researcher(
        self,
        db: AsyncSession,
        *,
        researcher_id: UUID,
        actor_user_id: UUID,
    ) -> bool:
        researcher = await self.get_researcher(db, researcher_id=researcher_id)
        if researcher is None:
            return False

        old_value = {
            "full_name": researcher.full_name,
            "email": researcher.email,
            "orcid": researcher.orcid,
            "department_id": str(researcher.department_id) if researcher.department_id else None,
            "academic_title": researcher.academic_title,
            "researcher_code": researcher.researcher_code,
            "is_internal": researcher.is_internal,
        }

        await db.delete(researcher)
        await db.flush()

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="DELETE_RESEARCHER",
            target_schema="reference",
            target_table="researchers",
            target_id=researcher_id,
            old_value=old_value,
            message="Deleted researcher",
        )

        return True


researcher_service = ResearcherService()
