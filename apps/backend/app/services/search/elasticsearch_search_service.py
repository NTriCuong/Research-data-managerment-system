import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.integrations.elasticsearch import get_elasticsearch_client


@dataclass(frozen=True, slots=True)
class ElasticsearchResearchHit:
    research_id: UUID
    score: float
    source: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ElasticsearchResearchPage:
    hits: list[ElasticsearchResearchHit]
    total: int


class ElasticsearchSearchError(RuntimeError):
    pass


class ElasticsearchSearchService:
    @staticmethod
    def _supports_fuzziness(query: str) -> bool:
        normalized = query.strip()
        return (
            len(normalized) >= 4
            and "@" not in normalized
            and not normalized.lower().startswith("doi:")
            and not normalized.lower().startswith("10.")
            and not _looks_like_uuid(normalized)
        )

    @classmethod
    def build_search_body(
        cls,
        *,
        query: str | None,
        access_filter: dict[str, Any] | None,
        output_type_ids: list[UUID] | None = None,
        department_ids: list[UUID] | None = None,
        domain_ids: list[UUID] | None = None,
        keyword_ids: list[UUID] | None = None,
        author_ids: list[UUID] | None = None,
        year: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        sort: str = "relevance",
        limit: int,
        offset: int,
    ) -> dict[str, Any]:
        filters: list[dict[str, Any]] = [{"term": {"is_current": True}}]
        if access_filter:
            filters.append(access_filter)
        if output_type_ids:
            filters.append({"terms": {"output_type.id": [str(value) for value in output_type_ids]}})
        if department_ids:
            filters.append({"terms": {"department.id": [str(value) for value in department_ids]}})
        if domain_ids:
            filters.append({"terms": {"domains.id": [str(value) for value in domain_ids]}})
        if keyword_ids:
            filters.append({"terms": {"keywords.id": [str(value) for value in keyword_ids]}})
        if author_ids:
            filters.append({"terms": {"authors.researcher_id": [str(value) for value in author_ids]}})
        if year is not None:
            filters.append({"term": {"year": year}})
        elif year_from is not None or year_to is not None:
            year_range: dict[str, int] = {}
            if year_from is not None:
                year_range["gte"] = year_from
            if year_to is not None:
                year_range["lte"] = year_to
            filters.append({"range": {"year": year_range}})

        normalized_query = query.strip() if query else ""
        bool_query: dict[str, Any] = {
            "filter": filters,
            "must_not": [{"exists": {"field": "deleted_at"}}],
        }
        if normalized_query:
            multi_match: dict[str, Any] = {
                "query": normalized_query,
                "type": "best_fields",
                "operator": "and",
                "fields": [
                    "title^6",
                    "title.accent^3",
                    "keywords.text^4",
                    "keywords.text.accent^2",
                    "authors.full_name^3",
                    "authors.full_name.accent^2",
                    "domains.name^2.5",
                    "domains.name.accent^1.5",
                    "abstract^2",
                    "description",
                    "department.name^1.5",
                    "output_type.name",
                    "publisher",
                ],
            }
            if cls._supports_fuzziness(normalized_query):
                multi_match.update({"fuzziness": "AUTO", "prefix_length": 2})

            bool_query.update(
                {
                    "should": [
                        {"match_phrase": {"title": {"query": normalized_query, "boost": 8}}},
                        {"multi_match": multi_match},
                        {
                            "multi_match": {
                                "query": normalized_query,
                                "type": "bool_prefix",
                                "fields": [
                                    "title.autocomplete^3",
                                    "authors.full_name.autocomplete^2",
                                    "identifier.autocomplete",
                                ],
                            }
                        },
                        {"match": {"identifier": {"query": normalized_query, "boost": 8}}},
                    ],
                    "minimum_should_match": 1,
                }
            )
        else:
            bool_query["must"] = {"match_all": {}}

        sort_options: dict[str, list[dict[str, str]]] = {
            "newest": [{"approved_at": "desc"}, {"created_at": "desc"}],
            "oldest": [{"approved_at": "asc"}, {"created_at": "asc"}],
            "most_viewed": [{"view_count": "desc"}, {"approved_at": "desc"}],
            "most_downloaded": [{"download_count": "desc"}, {"approved_at": "desc"}],
            "title_asc": [{"title.exact": "asc"}, {"approved_at": "desc"}],
            "relevance": [{"_score": "desc"}, {"approved_at": "desc"}],
        }

        return {
            "from": offset,
            "size": limit,
            "track_total_hits": True,
            "_source": [
                "research_id",
                "title",
                "year",
                "access_level",
                "version_no",
                "approved_at",
            ],
            "query": {"bool": bool_query},
            "sort": sort_options.get(sort, sort_options["relevance"]),
        }

    async def search_researches(
        self,
        *,
        query: str | None,
        access_filter: dict[str, Any] | None,
        output_type_ids: list[UUID] | None = None,
        department_ids: list[UUID] | None = None,
        domain_ids: list[UUID] | None = None,
        keyword_ids: list[UUID] | None = None,
        author_ids: list[UUID] | None = None,
        year: int | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        sort: str = "relevance",
        limit: int,
        offset: int,
    ) -> ElasticsearchResearchPage:
        body = self.build_search_body(
            query=query,
            access_filter=access_filter,
            output_type_ids=output_type_ids,
            department_ids=department_ids,
            domain_ids=domain_ids,
            keyword_ids=keyword_ids,
            author_ids=author_ids,
            year=year,
            year_from=year_from,
            year_to=year_to,
            sort=sort,
            limit=limit,
            offset=offset,
        )
        try:
            client = get_elasticsearch_client()
            response = await asyncio.to_thread(
                client.search,
                index=settings.ELASTIC_INDEX,
                body=body,
            )
            payload = response.body if hasattr(response, "body") else response
            raw_hits = payload.get("hits", {})
            raw_total = raw_hits.get("total", 0)
            total = int(raw_total.get("value", 0) if isinstance(raw_total, dict) else raw_total)
            hits = [
                ElasticsearchResearchHit(
                    research_id=UUID(str(item["_source"]["research_id"])),
                    score=float(item.get("_score") or 0.0),
                    source=item["_source"],
                )
                for item in raw_hits.get("hits", [])
            ]
            return ElasticsearchResearchPage(hits=hits, total=total)
        except Exception as exc:
            raise ElasticsearchSearchError("Elasticsearch search failed") from exc


def _looks_like_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


elasticsearch_search_service = ElasticsearchSearchService()
