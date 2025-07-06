from __future__ import annotations

from dataclasses import dataclass

import aiohttp
import asyncio
import logging
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

from application.api.dependencies import async_get_db
from application.api.schemas.stock_price import StockPriceCreate
from application.config.settings import settings
from infrastructure.database.models.stock_price import StockPrice
from load_symbols import load_symbols


TWELVEDATA_URL = settings.twelve_data_url
TWELVEDATA_API_KEY = settings.twelve_data_api_key

cfg = load_symbols()
INTERVAL = cfg.get("poll_interval_seconds", 1)
BATCH_TIME_INTERVAL = cfg.get("batch_time_interval", "1day")
START_DATE = cfg.get("start_date", 1)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("etl.batch")


@dataclass
class BatchDataProcessor:
    async def _fetch_daily(self, symbol: str) -> list[StockPriceCreate]:
        params = {
            "symbol": symbol,
            "interval": BATCH_TIME_INTERVAL,
            "outputsize": 250,
            "apikey": TWELVEDATA_API_KEY,
            "format": "JSON",
            "start_date": START_DATE,
        }
        async with aiohttp.ClientSession() as http:
            async with http.get(TWELVEDATA_URL, params=params) as resp:
                data = await resp.json()

        series = data.get("values", [])
        return [
            StockPriceCreate(
                ticker=symbol,
                timestamp=datetime.strptime(row["datetime"], "%Y-%m-%d"),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(float(row["volume"])),
            )
            for row in series
        ]

    async def process_data(self, symbol: str):
        log.info("Fetching %s stocks", symbol)
        prices = await self._fetch_daily(symbol)

        async for session in async_get_db():
            rows = [p.model_dump() for p in prices]
            stmt = insert(StockPrice).on_conflict_do_nothing(
                index_elements=["ticker", "timestamp"],
            )
            await session.execute(stmt, rows)
            await session.commit()
            log.info("Upserted %d rows for %s", len(rows), symbol)

    async def run_batch(self, symbols: list[str]):
        await asyncio.gather(
            *(self.process_data(symbol) for symbol in set(symbols)),
        )
        log.info("All stocks processed—shutting down.")
