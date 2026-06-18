from types import SimpleNamespace
from uuid import uuid4

from app.core.config import settings
from app.database.session import get_db
from app.services.auth import deps as auth_deps
from app.api.v1.endpoints import reference as reference_endpoint


class _FakeDbSession:
    pass


def _override_user_with_role(client, sample_user, role_code: str):
    sample_user.role = SimpleNamespace(role_code=role_code)

    async def _override_current_active_user():
        return sample_user

    client.app.dependency_overrides[auth_deps.get_current_active_user] = _override_current_active_user


def _fake_db_provider(db=None):
    fake_db = db or _FakeDbSession()

    async def _override_get_db():
        yield fake_db

    return _override_get_db


def test_data_entry_can_search_reference_suggestions(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    db = _FakeDbSession()
    client.app.dependency_overrides[get_db] = _fake_db_provider(db)

    domain_id = uuid4()
    keyword_id = uuid4()
    researcher_id = uuid4()
    captured = {}

    async def _fake_domains(db_arg, *, q, limit):
        captured["domains"] = {"db": db_arg, "q": q, "limit": limit}
        return [
            SimpleNamespace(
                domain_id=domain_id,
                domain_code="AI",
                domain_name="Artificial Intelligence",
                parent_domain_id=None,
                description=None,
                is_active=True,
            )
        ]

    async def _fake_keywords(db_arg, *, q, limit):
        captured["keywords"] = {"db": db_arg, "q": q, "limit": limit}
        return [
            SimpleNamespace(
                keyword_id=keyword_id,
                keyword_text="machine learning",
                normalized_text="machine learning",
            )
        ]

    async def _fake_researchers(db_arg, *, q, limit):
        captured["researchers"] = {"db": db_arg, "q": q, "limit": limit}
        return [
            SimpleNamespace(
                researcher_id=researcher_id,
                full_name="Nguyen Van A",
                email="a@example.com",
                orcid=None,
                department_id=None,
                academic_title=None,
                researcher_code="RES001",
                is_internal=True,
            )
        ]

    monkeypatch.setattr(reference_endpoint.research_domain_service, "suggest_research_domains", _fake_domains)
    monkeypatch.setattr(reference_endpoint.keyword_service, "suggest_keywords", _fake_keywords)
    monkeypatch.setattr(reference_endpoint.researcher_service, "suggest_researchers", _fake_researchers)

    prefix = settings.API_V1_PREFIX
    domain_response = client.get(f"{prefix}/reference/research-domains/suggestions", params={"q": "art", "limit": 7})
    keyword_response = client.get(f"{prefix}/reference/keywords/suggestions", params={"q": "machine", "limit": 8})
    researcher_response = client.get(f"{prefix}/reference/researchers/suggestions", params={"limit": 5})

    assert domain_response.status_code == 200
    assert domain_response.json()[0]["domain_id"] == str(domain_id)
    assert domain_response.json()[0]["domain_name"] == "Artificial Intelligence"
    assert captured["domains"] == {"db": db, "q": "art", "limit": 7}

    assert keyword_response.status_code == 200
    assert keyword_response.json()[0]["keyword_id"] == str(keyword_id)
    assert keyword_response.json()[0]["keyword_text"] == "machine learning"
    assert captured["keywords"] == {"db": db, "q": "machine", "limit": 8}

    assert researcher_response.status_code == 200
    assert researcher_response.json()[0]["researcher_id"] == str(researcher_id)
    assert researcher_response.json()[0]["full_name"] == "Nguyen Van A"
    assert captured["researchers"] == {"db": db, "q": None, "limit": 5}


def test_reviewer_can_read_keyword_suggestions(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "REVIEWER")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    async def _fake_keywords(*args, **kwargs):
        return []

    monkeypatch.setattr(reference_endpoint.keyword_service, "suggest_keywords", _fake_keywords)

    response = client.get(f"{settings.API_V1_PREFIX}/reference/keywords/suggestions")

    assert response.status_code == 200
    assert response.json() == []


def test_data_entry_can_create_domain_keyword_and_researcher_for_autocomplete_flow(client, sample_user, monkeypatch):
    _override_user_with_role(client, sample_user, "DATA_ENTRY")
    client.app.dependency_overrides[get_db] = _fake_db_provider()

    domain_id = uuid4()
    keyword_id = uuid4()
    researcher_id = uuid4()
    captured = {}

    async def _fake_create_domain(*args, **kwargs):
        captured["domain"] = kwargs
        return SimpleNamespace(
            domain_id=domain_id,
            domain_code=kwargs["domain_code"],
            domain_name=kwargs["domain_name"],
            parent_domain_id=kwargs["parent_domain_id"],
            description=kwargs["description"],
            is_active=kwargs["is_active"],
        )

    async def _fake_create_keyword(*args, **kwargs):
        captured["keyword"] = kwargs
        return SimpleNamespace(
            keyword_id=keyword_id,
            keyword_text=kwargs["keyword_text"],
            normalized_text=kwargs["normalized_text"],
        )

    async def _fake_create_researcher(*args, **kwargs):
        captured["researcher"] = kwargs
        return SimpleNamespace(
            researcher_id=researcher_id,
            full_name=kwargs["full_name"],
            email=kwargs["email"],
            orcid=kwargs["orcid"],
            department_id=kwargs["department_id"],
            academic_title=kwargs["academic_title"],
            researcher_code=kwargs["researcher_code"],
            is_internal=kwargs["is_internal"],
        )

    monkeypatch.setattr(reference_endpoint.research_domain_service, "create_research_domain", _fake_create_domain)
    monkeypatch.setattr(reference_endpoint.keyword_service, "create_keyword", _fake_create_keyword)
    monkeypatch.setattr(reference_endpoint.researcher_service, "create_researcher", _fake_create_researcher)

    prefix = settings.API_V1_PREFIX
    domain_response = client.post(
        f"{prefix}/reference/research-domains/",
        json={"domain_code": "NEW_AI", "domain_name": "New AI Domain"},
    )
    keyword_response = client.post(
        f"{prefix}/reference/keywords/",
        json={"keyword_text": "new keyword", "normalized_text": "new keyword"},
    )
    researcher_response = client.post(
        f"{prefix}/reference/researchers/",
        json={"full_name": "Tran Thi B", "email": "b@example.com", "is_internal": False},
    )

    assert domain_response.status_code == 201
    assert domain_response.json()["domain_id"] == str(domain_id)
    assert captured["domain"]["actor_user_id"] == sample_user.user_id

    assert keyword_response.status_code == 201
    assert keyword_response.json()["keyword_id"] == str(keyword_id)
    assert captured["keyword"]["actor_user_id"] == sample_user.user_id

    assert researcher_response.status_code == 201
    assert researcher_response.json()["researcher_id"] == str(researcher_id)
    assert captured["researcher"]["actor_user_id"] == sample_user.user_id
