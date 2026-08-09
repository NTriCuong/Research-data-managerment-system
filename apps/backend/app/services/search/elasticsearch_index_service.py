import asyncio
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.integrations.elasticsearch import create_elasticsearch_client
from app.models.core.core_research_object import CoreResearchObject
from app.models.core.core_research_object_domain import CoreResearchObjectDomain
from app.models.core.core_research_object_keyword import CoreResearchObjectKeyword


logger = logging.getLogger(__name__)


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return getattr(value, "value", value)


def _serialize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _serialize(item)
            for key, item in value.items()
            if item is not None
        }
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return _json_value(value)


def build_research_document(research: CoreResearchObject) -> dict[str, Any]:
    return _serialize(
        {
            "schema_version": 1,
            "research_id": research.research_id,
            "source_staging_id": research.source_staging_id,
            "title": research.title,
            "description": research.description,
            "abstract": research.abstract,
            "output_type": {
                "id": research.output_type.output_type_id,
                "code": research.output_type.type_code,
                "name": research.output_type.type_name,
            },
            "department": {
                "id": research.department.department_id,
                "code": research.department.department_code,
                "name": research.department.department_name,
            },
            "year": research.year,
            "start_date": research.start_date,
            "end_date": research.end_date,
            "date_issued": research.date_issued,
            "publisher": research.publisher,
            "language": research.language,
            "identifier": research.identifier,
            "external_url": research.external_url,
            "source": research.source,
            "relation": research.relation,
            "coverage": research.coverage,
            "rights": research.rights,
            "access_level": research.access_level,
            "authors": [
                {
                    "researcher_id": author.researcher_id,
                    "full_name": author.full_name,
                    "email": author.email,
                    "affiliation": author.affiliation,
                    "author_order": author.author_order,
                    "author_role": author.author_role,
                }
                for author in sorted(
                    research.authors,
                    key=lambda item: item.author_order,
                )
            ],
            "keywords": [
                {
                    "id": relation.keyword.keyword_id,
                    "text": relation.keyword.keyword_text,
                    "normalized_text": relation.keyword.normalized_text,
                }
                for relation in sorted(
                    research.keywords,
                    key=lambda item: item.keyword.keyword_text,
                )
            ],
            "domains": [
                {
                    "id": relation.domain.domain_id,
                    "code": relation.domain.domain_code,
                    "name": relation.domain.domain_name,
                }
                for relation in sorted(
                    research.domains,
                    key=lambda item: item.domain.domain_name,
                )
            ],
            "metadata_quality_score": research.metadata_quality_score,
            "view_count": research.view_count,
            "download_count": research.download_count,
            "version_no": research.version_no,
            "is_current": research.is_current,
            "approved_by": research.approved_by,
            "approved_at": research.approved_at,
            "created_at": research.created_at,
            "updated_at": research.updated_at,
            "deleted_at": research.deleted_at,
        }
    )


def _research_query(research_id: UUID):
    return (
        select(CoreResearchObject)
        .options(
            selectinload(CoreResearchObject.output_type),
            selectinload(CoreResearchObject.department),
            selectinload(CoreResearchObject.authors),
            selectinload(CoreResearchObject.domains).selectinload(
                CoreResearchObjectDomain.domain
            ),
            selectinload(CoreResearchObject.keywords).selectinload(
                CoreResearchObjectKeyword.keyword
            ),
        )
        .where(CoreResearchObject.research_id == research_id)
    )


async def index_research_document(research_id: UUID) -> None:
    """Synchronize one committed research record to Elasticsearch."""
    try:
        async with AsyncSessionLocal() as db:
            research = (
                await db.execute(_research_query(research_id))
            ).scalar_one_or_none()
            document = (
                build_research_document(research)
                if research is not None
                and research.deleted_at is None
                and research.is_current
                else None
            )

        client = create_elasticsearch_client()
        try:
            if document is None:
                await asyncio.to_thread(
                    client.options(ignore_status=404).delete,
                    index=settings.ELASTIC_INDEX,
                    id=str(research_id),
                )
            else:
                await asyncio.to_thread(
                    client.index,
                    index=settings.ELASTIC_INDEX,
                    id=str(research_id),
                    document=document,
                )
        finally:
            client.close()
    except Exception:
        logger.exception(
            "Failed to synchronize research %s to Elasticsearch",
            research_id,
        )
