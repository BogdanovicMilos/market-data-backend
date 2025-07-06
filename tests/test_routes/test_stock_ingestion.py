import asyncio
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from application.api.routers import stock_ingestion


@pytest.mark.asyncio
async def test_ingest_stock_data_triggers_batch(
    auth_headers, monkeypatch, client: AsyncClient
):
    """POST /api/ingestion schedules a background ETL run"""

    symbols = ["AAPL", "MSFT", "TSLA"]
    created = {}

    # Create a fake processor class that records the instance and uses AsyncMock for run_batch
    class FakeProcessor:
        def __init__(self):
            created["instance"] = self
            self.run_batch = AsyncMock(return_value=None)

    monkeypatch.setattr(
        stock_ingestion, "BatchDataProcessor", FakeProcessor, raising=False
    )

    # Call the ingestion endpoint
    response = await client.post("/api/ingestion", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "ETL process started in background"}

    await asyncio.sleep(0)

    processor = created.get("instance")
    assert processor is not None, "BatchDataProcessor was not instantiated"
    processor.run_batch.assert_awaited_once_with(symbols)
