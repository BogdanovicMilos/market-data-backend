import pytest
from httpx import ASGITransport, AsyncClient

from application.api.dependencies import async_get_db
from application.api.main import app


class TestClass:
    pass


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
    Override the async_get_db dependency so all routes receive a dummy DB session.
    """

    async def fake_get_db():
        yield None

    app.dependency_overrides[async_get_db] = fake_get_db
