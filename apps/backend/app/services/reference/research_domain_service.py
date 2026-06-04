from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.research_domain import ResearchDomain
from app.services.logs.audit_service import audit_service


class ResearchDomainService:
    async def list_research_domains(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[ResearchDomain], int]:
        offset = (page - 1) * page_size
        total = (await db.execute(select(func.count()).select_from(ResearchDomain))).scalar_one()
        result = await db.execute(
            select(ResearchDomain).order_by(ResearchDomain.domain_name.asc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_research_domain(self, db: AsyncSession, *, domain_id: UUID) -> ResearchDomain | None:
        result = await db.execute(select(ResearchDomain).where(ResearchDomain.domain_id == domain_id))
        return result.scalar_one_or_none()

    async def get_research_domain_by_code(self, db: AsyncSession, *, domain_code: str) -> ResearchDomain | None:
        result = await db.execute(select(ResearchDomain).where(ResearchDomain.domain_code == domain_code))
        return result.scalar_one_or_none()

    async def create_research_domain(
        self,
        db: AsyncSession,
        *,
        domain_code: str,
        domain_name: str,
        parent_domain_id: UUID | None,
        description: str | None,
        is_active: bool,
        actor_user_id: UUID,
    ) -> ResearchDomain:
        if await self.get_research_domain_by_code(db, domain_code=domain_code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="domain_code already exists")

        if parent_domain_id is not None:
            if await self.get_research_domain(db, domain_id=parent_domain_id) is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent domain not found")

        domain = ResearchDomain(
            domain_code=domain_code,
            domain_name=domain_name,
            parent_domain_id=parent_domain_id,
            description=description,
            is_active=is_active,
        )
        db.add(domain)
        await db.flush()
        await db.refresh(domain)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="CREATE_RESEARCH_DOMAIN",
            target_schema="reference",
            target_table="research_domains",
            target_id=domain.domain_id,
            new_value={
                "domain_code": domain.domain_code,
                "domain_name": domain.domain_name,
                "parent_domain_id": str(domain.parent_domain_id) if domain.parent_domain_id else None,
                "description": domain.description,
                "is_active": domain.is_active,
            },
            message="Created research domain",
        )

        return domain

    async def update_research_domain(
        self,
        db: AsyncSession,
        *,
        domain_id: UUID,
        actor_user_id: UUID,
        domain_code: str | None,
        domain_name: str | None,
        parent_domain_id: UUID | None,
        description: str | None,
        is_active: bool | None,
        fields_set: set[str],
    ) -> ResearchDomain | None:
        domain = await self.get_research_domain(db, domain_id=domain_id)
        if domain is None:
            return None

        old_value = {
            "domain_code": domain.domain_code,
            "domain_name": domain.domain_name,
            "parent_domain_id": str(domain.parent_domain_id) if domain.parent_domain_id else None,
            "description": domain.description,
            "is_active": domain.is_active,
        }

        if "parent_domain_id" in fields_set:
            if parent_domain_id == domain_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Domain cannot be its own parent")
            if parent_domain_id is not None:
                if await self.get_research_domain(db, domain_id=parent_domain_id) is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent domain not found")
            domain.parent_domain_id = parent_domain_id

        if "domain_code" in fields_set:
            if domain_code is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="domain_code cannot be null")
            existing = await self.get_research_domain_by_code(db, domain_code=domain_code)
            if existing and existing.domain_id != domain_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="domain_code already exists")
            domain.domain_code = domain_code

        if "domain_name" in fields_set:
            if domain_name is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="domain_name cannot be null")
            domain.domain_name = domain_name

        if "description" in fields_set:
            domain.description = description

        if "is_active" in fields_set:
            domain.is_active = bool(is_active)

        domain.updated_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(domain)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="UPDATE_RESEARCH_DOMAIN",
            target_schema="reference",
            target_table="research_domains",
            target_id=domain.domain_id,
            old_value=old_value,
            new_value={
                "domain_code": domain.domain_code,
                "domain_name": domain.domain_name,
                "parent_domain_id": str(domain.parent_domain_id) if domain.parent_domain_id else None,
                "description": domain.description,
                "is_active": domain.is_active,
            },
            message="Updated research domain",
        )

        return domain

    async def delete_research_domain(
        self,
        db: AsyncSession,
        *,
        domain_id: UUID,
        actor_user_id: UUID,
    ) -> bool:
        domain = await self.get_research_domain(db, domain_id=domain_id)
        if domain is None:
            return False

        old_value = {
            "domain_code": domain.domain_code,
            "domain_name": domain.domain_name,
            "parent_domain_id": str(domain.parent_domain_id) if domain.parent_domain_id else None,
            "description": domain.description,
            "is_active": domain.is_active,
        }

        await db.delete(domain)
        await db.flush()

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="DELETE_RESEARCH_DOMAIN",
            target_schema="reference",
            target_table="research_domains",
            target_id=domain_id,
            old_value=old_value,
            message="Deleted research domain",
        )

        return True


research_domain_service = ResearchDomainService()
