from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, String, UniqueConstraint

from application.api.dependencies.db import Base
from application.api.schemas.stock_price import StockPrice as StockPriceSchema
from infrastructure.database.utils import TimestampsMixin, UUIDMixin


class StockPrice(Base, UUIDMixin, TimestampsMixin):
    """
    Model class for StockPrice object
    """

    __tablename__ = "stock_prices"

    ticker = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    __table_args__ = (
        UniqueConstraint("ticker", "timestamp", name="uq_ticker_timestamp"),
    )

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_stock_price_response(self) -> StockPriceSchema:
        """
        Converts ORM object to Pydantic object
        """
        return StockPriceSchema(
            id=self.id,
            ticker=str(self.ticker),
            timestamp=self.timestamp,
            open=float(self.open),
            high=float(self.high),
            low=float(self.low),
            close=float(self.close),
            volume=float(self.volume),
        )
