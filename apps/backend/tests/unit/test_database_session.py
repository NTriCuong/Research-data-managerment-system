import pytest

from app.database import session as session_module


pytestmark = pytest.mark.asyncio


class FakeSession:
    def __init__(self) -> None:
        self.commit_count = 0
        self.rollback_count = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def commit(self) -> None:
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1


async def test_get_db_commits_after_success(monkeypatch):
    db = FakeSession()
    monkeypatch.setattr(session_module, "AsyncSessionLocal", lambda: db)

    provider = session_module.get_db()
    assert await anext(provider) is db

    with pytest.raises(StopAsyncIteration):
        await anext(provider)

    assert db.commit_count == 1
    assert db.rollback_count == 0


async def test_get_db_rolls_back_after_error(monkeypatch):
    db = FakeSession()
    monkeypatch.setattr(session_module, "AsyncSessionLocal", lambda: db)

    provider = session_module.get_db()
    assert await anext(provider) is db

    with pytest.raises(RuntimeError, match="request failed"):
        await provider.athrow(RuntimeError("request failed"))

    assert db.commit_count == 0
    assert db.rollback_count == 1
