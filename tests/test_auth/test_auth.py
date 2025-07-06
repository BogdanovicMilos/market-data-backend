import pytest
import uuid
from datetime import datetime
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture

from application.api.schemas.stock_price import StockPrice
from infrastructure.database.repositories.stock_price_repository import (
    StockPriceRepository,
)


class StockPriceRepositoryPrepopulated(StockPriceRepository):
    def __init__(self, _=None):
        super().__init__(db=None)
        now = datetime(2025, 1, 1, 12, 0)
        self._prices = [
            StockPrice(
                id=uuid.UUID(int=1),
                ticker="AAPL",
                timestamp=now,
                open=100.0,
                high=110.0,
                low=90.0,
                close=105.0,
                volume=1000,
            ),
            StockPrice(
                id=uuid.UUID(int=2),
                ticker="TSLA",
                timestamp=now,
                open=200.0,
                high=210.0,
                low=190.0,
                close=205.0,
                volume=2000,
            ),
        ]

    async def get_stock_prices(
        self, skip: int = 0, limit: int = 100
    ) -> list[StockPrice]:
        return self._prices[skip : skip + limit]

    async def get_stock_prices_by_date_range(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> list[StockPrice]:
        return [
            p
            for p in self._prices
            if (start is None or p.timestamp >= start)
            and (end is None or p.timestamp <= end)
        ]


@pytest.mark.asyncio
async def test_no_auth_header_returns_401(
    mocker: MockerFixture, client: AsyncClient
):
    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )

    response = await client.get("/api/stock/prices")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or missing bearer token"


@pytest.mark.asyncio
async def test_invalid_token_returns_401(
    mocker: MockerFixture, client: AsyncClient
):
    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )

    headers = {"Authorization": "Bearer WRONG_TOKEN"}
    response = await client.get("/api/stock/prices", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid or missing bearer token"


@pytest.mark.asyncio
async def test_valid_token_allows_access(
    auth_headers,
    mocker: MockerFixture,
    client: AsyncClient,
):
    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )

    response = await client.get("/api/stock/prices", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_valid_token_on_search(
    auth_headers,
    mocker: MockerFixture,
    client: AsyncClient,
):
    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )

    params = {"start": "2025-01-01T00:00:00", "end": "2025-01-02T00:00:00"}
    response = await client.get(
        "/api/stock/search", headers=auth_headers, params=params
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
