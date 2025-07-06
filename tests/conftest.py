import os
import pytest
from httpx import ASGITransport, AsyncClient

from application.api.dependencies.db import async_get_db
from application.api.main import app


class TestClass:
    pass


@pytest.fixture
def auth_headers(monkeypatch):
    monkeypatch.setenv("VALID_BEARER_TOKEN", "TestToken123")
    token = os.getenv("VALID_BEARER_TOKEN")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_db():
    """
    Override the async_get_db dependency so all routes receive a fake DB session.
    """

    async def fake_get_db():
        yield None

    app.dependency_overrides[async_get_db] = fake_get_db
