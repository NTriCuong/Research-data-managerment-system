from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.config import settings
from app.services.search import elasticsearch_index_service as index_module


def _research(**overrides):
    values = {
        "research_id": uuid4(),
        "source_staging_id": uuid4(),
        "title": "Searchable research",
        "description": "Description",
        "abstract": "Abstract",
        "output_type": SimpleNamespace(
            output_type_id=uuid4(),
            type_code="ARTICLE",
            type_name="Article",
        ),
        "department": SimpleNamespace(
            department_id=uuid4(),
            department_code="IT",
            department_name="Information Technology",
        ),
        "year": 2026,
        "start_date": None,
        "end_date": None,
        "date_issued": None,
        "publisher": None,
        "language": "vi",
        "identifier": "RDMS-001",
        "external_url": None,
        "source": None,
        "relation": None,
        "coverage": None,
        "rights": None,
        "access_level": SimpleNamespace(value="public"),
        "authors": [
            SimpleNamespace(
                researcher_id=uuid4(),
                full_name="Nguyen Van A",
                email="a@example.com",
                affiliation="STU",
                author_order=1,
                author_role=SimpleNamespace(value="creator"),
            )
        ],
        "keywords": [
            SimpleNamespace(
                keyword=SimpleNamespace(
                    keyword_id=uuid4(),
                    keyword_text="Elasticsearch",
                    normalized_text="elasticsearch",
                )
            )
        ],
        "domains": [
            SimpleNamespace(
                domain=SimpleNamespace(
                    domain_id=uuid4(),
                    domain_code="CS",
                    domain_name="Computer Science",
                )
            )
        ],
        "metadata_quality_score": None,
        "view_count": 3,
        "download_count": 2,
        "version_no": 1,
        "is_current": True,
        "approved_by": uuid4(),
        "approved_at": datetime(2026, 8, 9, tzinfo=timezone.utc),
        "created_at": datetime(2026, 8, 9, tzinfo=timezone.utc),
        "updated_at": None,
        "deleted_at": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class _Result:
    def __init__(self, research):
        self.research = research

    def scalar_one_or_none(self):
        return self.research


class _Session:
    def __init__(self, research):
        self.research = research

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def execute(self, _statement):
        return _Result(self.research)


class _Client:
    def __init__(self):
        self.index_calls = []
        self.delete_calls = []
        self.closed = False

    def index(self, **kwargs):
        self.index_calls.append(kwargs)

    def options(self, **_kwargs):
        return self

    def delete(self, **kwargs):
        self.delete_calls.append(kwargs)

    def close(self):
        self.closed = True


@pytest.mark.anyio
async def test_index_task_reads_committed_record_and_upserts_by_database_id(monkeypatch):
    research = _research()
    client = _Client()
    monkeypatch.setattr(index_module, "AsyncSessionLocal", lambda: _Session(research))
    monkeypatch.setattr(index_module, "create_elasticsearch_client", lambda: client)

    await index_module.index_research_document(research.research_id)

    assert client.delete_calls == []
    assert len(client.index_calls) == 1
    request = client.index_calls[0]
    assert request["index"] == settings.ELASTIC_INDEX
    assert request["id"] == str(research.research_id)
    assert request["document"]["research_id"] == str(research.research_id)
    assert request["document"]["access_level"] == "public"
    assert client.closed is True


@pytest.mark.anyio
async def test_index_task_deletes_document_when_record_no_longer_exists(monkeypatch):
    research_id = uuid4()
    client = _Client()
    monkeypatch.setattr(index_module, "AsyncSessionLocal", lambda: _Session(None))
    monkeypatch.setattr(index_module, "create_elasticsearch_client", lambda: client)

    await index_module.index_research_document(research_id)

    assert client.index_calls == []
    assert client.delete_calls == [
        {"index": settings.ELASTIC_INDEX, "id": str(research_id)}
    ]
    assert client.closed is True
