from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.models.enum import AccessLevel
from app.schemas.public_research import PublicResearchListOut
from app.schemas.search import CoreSearchResponseOut
from app.services.core.public_research_service import PublicResearchService
from app.services.search import elasticsearch_search_service as elastic_module
from app.services.search.elasticsearch_search_service import (
    ElasticsearchResearchHit,
    ElasticsearchResearchPage,
    ElasticsearchSearchError,
    ElasticsearchSearchService,
)
from app.services.search.search_service import SearchService


def _find_filter(body: dict, field: str) -> dict | None:
    for clause in body["query"]["bool"]["filter"]:
        if field in clause.get("term", {}) or field in clause.get("terms", {}):
            return clause
    return None


def test_build_search_body_uses_bm25_filters_and_pagination():
    output_type_id = uuid4()
    department_id = uuid4()
    domain_id = uuid4()
    keyword_id = uuid4()
    author_id = uuid4()

    body = ElasticsearchSearchService.build_search_body(
        query="tri tue nhan tao",
        access_filter={"term": {"access_level": "public"}},
        output_type_ids=[output_type_id],
        department_ids=[department_id],
        domain_ids=[domain_id],
        keyword_ids=[keyword_id],
        author_ids=[author_id],
        year=2026,
        sort="most_viewed",
        limit=12,
        offset=24,
    )

    assert body["from"] == 24
    assert body["size"] == 12
    assert body["track_total_hits"] is True
    assert _find_filter(body, "access_level") == {"term": {"access_level": "public"}}
    assert _find_filter(body, "output_type.id") == {"terms": {"output_type.id": [str(output_type_id)]}}
    assert _find_filter(body, "department.id") == {"terms": {"department.id": [str(department_id)]}}
    assert _find_filter(body, "domains.id") == {"terms": {"domains.id": [str(domain_id)]}}
    assert _find_filter(body, "keywords.id") == {"terms": {"keywords.id": [str(keyword_id)]}}
    assert _find_filter(body, "authors.researcher_id") == {
        "terms": {"authors.researcher_id": [str(author_id)]}
    }
    assert _find_filter(body, "year") == {"term": {"year": 2026}}
    assert body["sort"] == [{"view_count": "desc"}, {"approved_at": "desc"}]
    assert body["query"]["bool"]["minimum_should_match"] == 1
    assert body["query"]["bool"]["must_not"] == [{"exists": {"field": "deleted_at"}}]


def test_build_search_body_supports_year_range_and_title_sort():
    body = ElasticsearchSearchService.build_search_body(
        query=None,
        access_filter=None,
        year_from=2020,
        year_to=2026,
        sort="title_asc",
        limit=12,
        offset=0,
    )

    assert {"range": {"year": {"gte": 2020, "lte": 2026}}} in body["query"]["bool"]["filter"]
    assert body["sort"] == [{"title.exact": "asc"}, {"approved_at": "desc"}]


@pytest.mark.parametrize("query", ["AI", "ada@example.com", "10.1000/test"])
def test_short_identifier_and_email_queries_do_not_enable_fuzziness(query):
    body = ElasticsearchSearchService.build_search_body(
        query=query,
        access_filter=None,
        limit=10,
        offset=0,
    )

    multi_match = body["query"]["bool"]["should"][1]["multi_match"]
    assert "fuzziness" not in multi_match


class _FakeElasticsearchClient:
    def __init__(self, research_id: UUID):
        self.research_id = research_id
        self.search_kwargs = None
        self.closed = False

    def search(self, **kwargs):
        self.search_kwargs = kwargs
        return {
            "hits": {
                "total": {"value": 1, "relation": "eq"},
                "hits": [
                    {
                        "_score": 4.25,
                        "_source": {
                            "research_id": str(self.research_id),
                            "title": "Artificial Intelligence",
                        },
                    }
                ],
            }
        }

    def close(self):
        self.closed = True


@pytest.mark.anyio
async def test_search_researches_parses_hits_and_reuses_client(monkeypatch):
    research_id = uuid4()
    client = _FakeElasticsearchClient(research_id)
    monkeypatch.setattr(elastic_module, "get_elasticsearch_client", lambda: client)

    page = await ElasticsearchSearchService().search_researches(
        query="artificial intelligence",
        access_filter={"term": {"access_level": "public"}},
        limit=20,
        offset=0,
    )

    assert page.total == 1
    assert page.hits[0].research_id == research_id
    assert page.hits[0].score == 4.25
    assert client.search_kwargs["index"] == elastic_module.settings.ELASTIC_INDEX
    assert client.closed is False


@pytest.mark.anyio
async def test_core_search_falls_back_to_postgres(monkeypatch):
    service = SearchService()
    calls = []

    async def _elastic(*_args, **_kwargs):
        calls.append("elastic")
        raise ElasticsearchSearchError("unavailable")

    async def _postgres(*_args, **kwargs):
        calls.append("postgres")
        return CoreSearchResponseOut(
            items=[],
            total=kwargs["limit"],
            limit=kwargs["limit"],
            offset=kwargs["offset"],
        )

    monkeypatch.setattr(service, "search_core_elasticsearch", _elastic)
    monkeypatch.setattr(service, "search_core_postgres", _postgres)

    result = await service.search_core(object(), query="benchmark", limit=10, offset=0)

    assert calls == ["elastic", "postgres"]
    assert result.total == 10


class _CoreHydrationResult:
    def __init__(self, core_object):
        self.core_object = core_object

    def scalars(self):
        return self

    def all(self):
        return [self.core_object]


class _CoreHydrationDb:
    def __init__(self, core_object):
        self.core_object = core_object
        self.statement = None

    async def execute(self, statement):
        self.statement = statement
        return _CoreHydrationResult(self.core_object)


@pytest.mark.anyio
async def test_core_elasticsearch_search_hydrates_authoritative_postgres_record(monkeypatch):
    research_id = uuid4()
    approved_at = datetime(2026, 8, 4, tzinfo=timezone.utc)
    core_object = SimpleNamespace(
        research_id=research_id,
        title="Authoritative title",
        year=2026,
        access_level=AccessLevel.public,
        version_no=3,
        approved_at=approved_at,
    )
    db = _CoreHydrationDb(core_object)
    current_user = SimpleNamespace(role=SimpleNamespace(role_code="MANAGER"))

    async def _search(**_kwargs):
        return ElasticsearchResearchPage(
            hits=[
                ElasticsearchResearchHit(
                    research_id=research_id,
                    score=7.5,
                    source={"research_id": str(research_id), "title": "Stale indexed title"},
                )
            ],
            total=1,
        )

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)

    response = await SearchService().search_core_elasticsearch(
        db,
        query="authoritative",
        limit=20,
        offset=0,
        current_user=current_user,
    )

    assert response.total == 1
    assert response.items[0].title == "Authoritative title"
    assert response.items[0].rank == 7.5
    assert db.statement is not None


@pytest.mark.anyio
async def test_public_filters_use_elasticsearch(monkeypatch):
    output_type_id = uuid4()
    captured = {}

    async def _search(**kwargs):
        captured.update(kwargs)
        return ElasticsearchResearchPage(hits=[], total=0)

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)

    response = await PublicResearchService().list_public_researches(
        object(),
        q=None,
        output_type_ids=[output_type_id],
        department_ids=None,
        domain_ids=None,
        keyword_ids=None,
        author_ids=None,
        year_from=2026,
        year_to=2026,
        has_files=False,
        sort="newest",
        limit=12,
        offset=0,
    )

    assert response == PublicResearchListOut(items=[], total=0, limit=12, offset=0)
    assert captured["query"] is None
    assert captured["output_type_ids"] == [output_type_id]
    assert captured["year_from"] == 2026
    assert captured["year_to"] == 2026
    assert captured["sort"] == "newest"
    assert captured["access_filter"] == {"term": {"access_level": "public"}}


@pytest.mark.anyio
async def test_public_search_falls_back_to_postgres(monkeypatch):
    service = PublicResearchService()

    async def _search(**_kwargs):
        raise ElasticsearchSearchError("unavailable")

    async def _postgres(*_args, **kwargs):
        return PublicResearchListOut(
            items=[],
            total=2,
            limit=kwargs["limit"],
            offset=kwargs["offset"],
        )

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)
    monkeypatch.setattr(service, "_list_public_researches_postgres", _postgres)

    response = await service.list_public_researches(
        object(),
        q="benchmark",
        output_type_ids=None,
        department_ids=None,
        domain_ids=None,
        keyword_ids=None,
        author_ids=None,
        year_from=None,
        year_to=None,
        has_files=False,
        sort="relevance",
        limit=12,
        offset=0,
    )

    assert response.total == 2


@pytest.mark.anyio
async def test_public_has_files_filter_uses_postgres(monkeypatch):
    service = PublicResearchService()
    captured = {}

    async def _search(**_kwargs):
        raise AssertionError("Elasticsearch must not be used for has_files")

    async def _postgres(*_args, **kwargs):
        captured.update(kwargs)
        return PublicResearchListOut(items=[], total=3, limit=kwargs["limit"], offset=kwargs["offset"])

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)
    monkeypatch.setattr(service, "_list_public_researches_postgres", _postgres)

    response = await service.list_public_researches(
        object(),
        q=None,
        output_type_ids=None,
        department_ids=None,
        domain_ids=None,
        keyword_ids=None,
        author_ids=None,
        year_from=None,
        year_to=None,
        has_files=True,
        sort="newest",
        limit=12,
        offset=0,
    )

    assert response.total == 3
    assert captured["has_files"] is True


@pytest.mark.anyio
async def test_public_suggestions_use_elasticsearch_and_hydrate_postgres(monkeypatch):
    research_id = uuid4()
    db = _CoreHydrationDb(
        SimpleNamespace(
            research_id=research_id,
            title="Authoritative suggestion",
            year=2026,
        )
    )
    captured = {}

    async def _search(**kwargs):
        captured.update(kwargs)
        return ElasticsearchResearchPage(
            hits=[
                ElasticsearchResearchHit(
                    research_id=research_id,
                    score=6.0,
                    source={"research_id": str(research_id), "title": "Stale suggestion"},
                )
            ],
            total=1,
        )

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)

    response = await PublicResearchService().suggest_public_researches(
        db,
        q="author",
        limit=8,
    )

    assert response[0].research_id == research_id
    assert response[0].title == "Authoritative suggestion"
    assert captured["query"] == "author"
    assert captured["access_filter"] == {"term": {"access_level": "public"}}
    assert captured["limit"] == 8
    assert captured["offset"] == 0


@pytest.mark.anyio
async def test_public_suggestions_fall_back_to_postgres(monkeypatch):
    service = PublicResearchService()
    expected = []

    async def _search(**_kwargs):
        raise ElasticsearchSearchError("unavailable")

    async def _postgres(*_args, **kwargs):
        assert kwargs == {"q": "benchmark", "limit": 5}
        return expected

    monkeypatch.setattr(elastic_module.elasticsearch_search_service, "search_researches", _search)
    monkeypatch.setattr(service, "_suggest_public_researches_postgres", _postgres)

    response = await service.suggest_public_researches(
        object(),
        q="benchmark",
        limit=5,
    )

    assert response is expected
