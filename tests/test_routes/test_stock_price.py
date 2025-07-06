import pytest
import uuid
from datetime import datetime
from fastapi import HTTPException
from httpx import AsyncClient
from pytest_mock import MockerFixture
from starlette import status

from application.api.schemas.stock_price import StockPrice, StockPriceCreate
from infrastructure.database.repositories.stock_price_repository import (
    StockPriceRepository,
)


class StockPriceRepositoryPrepopulated(StockPriceRepository):
    def __init__(self, _=None):
        super().__init__(db=None)
        # Seed two entries for ticker "AAPL" and "TSLA"
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

    async def get_stock_price_by_id(
        self, stock_price_id: uuid.UUID
    ) -> StockPrice:
        for p in self._prices:
            if p.id == stock_price_id:
                return p
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stock price found",
        )

    async def get_stock_prices_by_ticker(
        self, ticker: str
    ) -> list[StockPrice]:
        matches = [p for p in self._prices if p.ticker == ticker]
        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock prices found for ticker",
            )
        return matches

    async def create_stock_price(
        self, stock_price: StockPriceCreate
    ) -> StockPrice:
        new = StockPrice(**stock_price.model_dump())
        new.id = uuid.uuid4()
        self._prices.append(new)
        return new

    async def delete_stock_price(self, stock_price_id: uuid.UUID) -> bool:
        for idx, p in enumerate(self._prices):
            if p.id == stock_price_id:
                self._prices.pop(idx)
                return True
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stock price found to delete",
        )

    async def update_stock_price(
        self, stock_price_id: uuid.UUID, stock_price_payload: dict
    ) -> StockPrice:
        for p in self._prices:
            if p.id == stock_price_id:
                for field, value in stock_price_payload.items():
                    setattr(p, field, value)
                return p
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No stock price found to update",
        )


@pytest.mark.asyncio
async def test_get_all(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/prices returns all seeded prices"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )

    response = await client.get("/api/stock/prices", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_price_by_id(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/{id} returns the correct price"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    test_id = str(uuid.UUID(int=1))
    response = await client.get(f"/api/stock/{test_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_id
    assert data["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_prices_by_date_range(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/search?start=...&end=... filters by date range"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    # Seeded timestamp is 2025-01-01T12:00:00
    start = "2025-01-01T00:00:00"
    end = "2025-01-02T00:00:00"
    response = await client.get(
        f"/api/stock/search?start={start}&end={end}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_prices_by_date_range_no_match(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/search outside the seeded date returns empty list"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    # Range with no overlapping timestamp
    start = "2024-01-01T00:00:00"
    end = "2024-12-31T23:59:59"
    response = await client.get(
        f"/api/stock/search?start={start}&end={end}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_pagination_skip(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/prices?skip=1 skips the first result"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    response = await client.get(
        "/api/stock/prices?skip=1", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(uuid.UUID(int=2))


@pytest.mark.asyncio
async def test_pagination_limit(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/prices?limit=1 limits to a single result"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    response = await client.get(
        "/api/stock/prices?limit=1", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_nonexistent_price_by_id(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/{id} with unknown id returns 404"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    nonexist_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/stock/{nonexist_id}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_invalid_uuid_returns_422(
    auth_headers, mocker: MockerFixture, client: AsyncClient
):
    """GET /api/stock/{id} with invalid UUID returns 422"""

    mocker.patch(
        "application.api.routers.stock_price.StockPriceRepository",
        StockPriceRepositoryPrepopulated,
    )
    response = await client.get("/api/stock/not-a-uuid", headers=auth_headers)
    assert response.status_code == 422
