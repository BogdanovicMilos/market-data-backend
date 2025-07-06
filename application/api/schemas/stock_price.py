from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class StockPrice(BaseModel):
    id: uuid.UUID
    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    model_config = ConfigDict(from_attributes=True)


class StockPriceUpdate(BaseModel):
    ticker: str | None = None
    timestamp: datetime | None = None
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None

    @classmethod
    @field_validator("timestamp")
    def no_future_dates(cls, value: datetime):
        if value and value > datetime.utcnow():
            raise ValueError("timestamp cannot be in the future")
        return value


class StockPriceCreate(BaseModel):
    ticker: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
