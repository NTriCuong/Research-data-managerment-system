from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reference.keyword import Keyword
from app.services.logs.audit_service import audit_service


class KeywordService:
    async def list_keywords(self, db: AsyncSession) -> list[Keyword]:
        result = await db.execute(select(Keyword).order_by(Keyword.keyword_text.asc()))
        return list(result.scalars().all())

    async def get_keyword(self, db: AsyncSession, *, keyword_id: UUID) -> Keyword | None:
        result = await db.execute(select(Keyword).where(Keyword.keyword_id == keyword_id))
        return result.scalar_one_or_none()

    async def get_keyword_by_text(self, db: AsyncSession, *, keyword_text: str) -> Keyword | None:
        result = await db.execute(select(Keyword).where(Keyword.keyword_text == keyword_text))
        return result.scalar_one_or_none()

    async def create_keyword(
        self,
        db: AsyncSession,
        *,
        keyword_text: str,
        normalized_text: str | None,
        actor_user_id: UUID,
    ) -> Keyword:
        if await self.get_keyword_by_text(db, keyword_text=keyword_text):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="keyword_text already exists")

        keyword = Keyword(
            keyword_text=keyword_text,
            normalized_text=normalized_text,
        )
        db.add(keyword)
        await db.flush()
        await db.refresh(keyword)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="CREATE_KEYWORD",
            target_schema="reference",
            target_table="keywords",
            target_id=keyword.keyword_id,
            new_value={"keyword_text": keyword.keyword_text, "normalized_text": keyword.normalized_text},
            message="Created keyword",
        )

        return keyword

    async def update_keyword(
        self,
        db: AsyncSession,
        *,
        keyword_id: UUID,
        actor_user_id: UUID,
        keyword_text: str | None,
        normalized_text: str | None,
        fields_set: set[str],
    ) -> Keyword | None:
        keyword = await self.get_keyword(db, keyword_id=keyword_id)
        if keyword is None:
            return None

        old_value = {"keyword_text": keyword.keyword_text, "normalized_text": keyword.normalized_text}

        if "keyword_text" in fields_set:
            if keyword_text is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="keyword_text cannot be null")
            existing = await self.get_keyword_by_text(db, keyword_text=keyword_text)
            if existing and existing.keyword_id != keyword_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="keyword_text already exists")
            keyword.keyword_text = keyword_text

        if "normalized_text" in fields_set:
            keyword.normalized_text = normalized_text

        await db.flush()
        await db.refresh(keyword)

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="UPDATE_KEYWORD",
            target_schema="reference",
            target_table="keywords",
            target_id=keyword.keyword_id,
            old_value=old_value,
            new_value={"keyword_text": keyword.keyword_text, "normalized_text": keyword.normalized_text},
            message="Updated keyword",
        )

        return keyword

    async def delete_keyword(
        self,
        db: AsyncSession,
        *,
        keyword_id: UUID,
        actor_user_id: UUID,
    ) -> bool:
        keyword = await self.get_keyword(db, keyword_id=keyword_id)
        if keyword is None:
            return False

        old_value = {"keyword_text": keyword.keyword_text, "normalized_text": keyword.normalized_text}

        await db.delete(keyword)
        await db.flush()

        await audit_service.write_log(
            db,
            actor_user_id=actor_user_id,
            action_code="DELETE_KEYWORD",
            target_schema="reference",
            target_table="keywords",
            target_id=keyword_id,
            old_value=old_value,
            message="Deleted keyword",
        )

        return True


keyword_service = KeywordService()
