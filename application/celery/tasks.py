import asyncio
import io
import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from application.api.dependencies.db import async_get_db
from application.celery.main import celery
from infrastructure.database.models.stock_price import StockPrice


async def _load_dataframe_async(df: pd.DataFrame):
    """
    Asynchronously load a DataFrame into the database
    """

    table = StockPrice.__table__

    async for session in async_get_db():
        records = []
        for row in df.itertuples(index=False):
            records.append(
                {
                    "ticker": row.ticker,
                    "timestamp": row.timestamp.to_pydatetime(),
                    "open": round(float(row.open), 2),
                    "high": round(float(row.high), 2),
                    "low": round(float(row.low), 2),
                    "close": round(float(row.close), 2),
                    "volume": float(row.volume),
                }
            )
        stmt = (
            insert(table)
            .values(records)
            .on_conflict_do_update(
                index_elements=["ticker", "timestamp"],
                set_={
                    "open": insert(table).excluded.open,
                    "high": insert(table).excluded.high,
                    "low": insert(table).excluded.low,
                    "close": insert(table).excluded.close,
                    "volume": insert(table).excluded.volume,
                },
            )
        )
        await session.execute(stmt)
        await session.commit()


@celery.task(bind=True, max_retries=3, name="process_stocks_data_csv")
def process_stocks_data_task(self, csv_data: str):
    """
    Celery task to parse a CSV string and load rows into a database.
    Retries up to 3 times on failure, with a 60-second backoff.
    """
    try:
        df = pd.read_csv(io.StringIO(csv_data), parse_dates=["datetime"])
        df = df.rename(
            columns={
                "symbol": "ticker",
                "datetime": "timestamp",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            }
        ).dropna(subset=["ticker", "timestamp", "close"])

        asyncio.run(_load_dataframe_async(df))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
