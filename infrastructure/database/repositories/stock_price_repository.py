from __future__ import annotations

from dataclasses import dataclass

import logging
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from uuid import UUID

from application.api.schemas.stock_price import StockPriceCreate
from infrastructure.database.models.stock_price import StockPrice


log = logging.getLogger("repository.stock_price")


@dataclass
class StockPriceRepository:
    db: AsyncSession

    async def get_stock_prices(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[StockPrice]:
        """Retrieve stock prices"""

        statement = select(StockPrice).offset(skip).limit(limit)

        try:
            result = await self.db.execute(statement)
        except SQLAlchemyError as exc:
            log.error("Error fetching stock prices: %s", exc)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database query failed",
            ) from exc

        prices = result.scalars().all()

        if not prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock prices found",
            )

        return list(prices)

    async def get_stock_prices_by_date_range(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[StockPrice]:
        """Retrieve stock prices by date range"""

        statement = select(StockPrice)

        if start:
            statement = statement.where(StockPrice.timestamp >= start)
        if end:
            statement = statement.where(StockPrice.timestamp <= end)

        result = await self.db.execute(statement)
        prices = result.scalars().all()
        return list(prices)

    async def get_stock_price_by_id(
        self,
        stock_price_id: UUID,
    ) -> StockPrice:
        """Get stock price"""

        statement = select(StockPrice).where(StockPrice.id == stock_price_id)

        try:
            result = await self.db.execute(statement)
        except SQLAlchemyError as exc:
            log.error("Error fetching stock price: %s", exc)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database query failed",
            ) from exc

        price = result.scalars().first()

        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock price founded",
            )

        return price

    async def get_stock_prices_by_ticker(
        self,
        ticker: str,
    ) -> list[StockPrice]:
        """Get stock prices by ticker symbol"""

        statement = select(StockPrice).where(StockPrice.ticker == ticker)

        try:
            result = await self.db.execute(statement)
        except SQLAlchemyError as exc:
            log.error("Error fetching stock price: %s", exc)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database query failed",
            ) from exc

        prices = result.scalars().all()

        if not prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock prices found",
            )

        return list(prices)

    async def create_stock_price(
        self,
        stock_price: StockPriceCreate,
    ) -> StockPrice:
        """Create new stock price"""

        price = StockPrice(**stock_price.model_dump())

        try:
            self.db.add(price)
            await self.db.commit()
            await self.db.refresh(price)
            return price

        except SQLAlchemyError as exc:
            log.error("Error creating stock price: %s", exc)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database creation failed",
            ) from exc

    async def delete_stock_price(self, stock_price_id: UUID) -> bool:
        """Delete stock price"""

        price = await self.get_stock_price_by_id(stock_price_id)

        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock price found",
            )

        await self.db.delete(price)
        await self.db.commit()
        return True

    async def update_stock_price(
        self,
        stock_price_id: UUID,
        stock_price_payload: dict,
    ) -> StockPrice:
        """Update stock price"""

        price = await self.get_stock_price_by_id(stock_price_id)

        if not price:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stock price found",
            )

        try:
            for field, value in stock_price_payload.items():
                setattr(price, field, value)
            await self.db.commit()
            await self.db.refresh(price)
            return price

        except SQLAlchemyError as exc:
            log.error("Error updating stock price: %s", exc)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stock market update failed",
            ) from exc
