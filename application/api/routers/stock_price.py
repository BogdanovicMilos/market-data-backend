from __future__ import annotations

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from application.api.dependencies.db import async_get_db
from application.api.dependencies.middleware import token_auth_middleware
from application.api.schemas.stock_price import (
    StockPrice,
    StockPriceCreate,
    StockPriceUpdate,
)
from infrastructure.database.repositories.stock_price_repository import (
    StockPriceRepository,
)


router = APIRouter(
    prefix="/api/stock",
    tags=["Stocks"],
    dependencies=[Depends(token_auth_middleware)],
)

log = logging.getLogger("stock_price")


@router.get(
    "/search",
    response_model=list[StockPrice],
    status_code=status.HTTP_200_OK,
)
async def search_prices(
    start: datetime | None = Query(None, description="Start of time range"),
    end: datetime | None = Query(None, description="End of time range"),
    db: AsyncSession = Depends(async_get_db),
) -> list[StockPrice]:
    stock_price_repository = StockPriceRepository(db)
    return await stock_price_repository.get_stock_prices_by_date_range(
        start,
        end,
    )


@router.get(
    "/prices",
    response_model=list[StockPrice],
    status_code=status.HTTP_200_OK,
)
async def read_prices(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(async_get_db),
) -> list[StockPrice]:
    stock_price_repository = StockPriceRepository(db)
    return await stock_price_repository.get_stock_prices(skip, limit)


@router.get(
    "/{stock_price_id}",
    response_model=StockPrice,
    status_code=status.HTTP_200_OK,
)
async def read_price_by_id(
    stock_price_id: UUID,
    db: AsyncSession = Depends(async_get_db),
) -> StockPrice:
    stock_price_repository = StockPriceRepository(db)
    return await stock_price_repository.get_stock_price_by_id(stock_price_id)


@router.get(
    "/ticker/{ticker}",
    response_model=list[StockPrice],
    status_code=status.HTTP_200_OK,
)
async def read_by_ticker(
    ticker: str,
    db: AsyncSession = Depends(async_get_db),
) -> list[StockPrice]:
    stock_price_repository = StockPriceRepository(db)
    return await stock_price_repository.get_stock_prices_by_ticker(ticker)


@router.post(
    "/create",
    response_model=StockPrice,
    status_code=status.HTTP_201_CREATED,
)
async def create_price(
    stock_price: StockPriceCreate,
    db: AsyncSession = Depends(async_get_db),
):
    stock_price_repository = StockPriceRepository(db)
    return await stock_price_repository.create_stock_price(stock_price)


@router.put(
    "/{stock_price_id}",
    response_model=StockPrice,
    status_code=status.HTTP_200_OK,
)
async def update_stock_price(
    stock_price_id: UUID,
    payload: StockPriceUpdate,
    db: AsyncSession = Depends(async_get_db),
) -> StockPrice:
    stock_price_repository = StockPriceRepository(db)
    stock_price_payload = payload.model_dump(exclude_unset=True)

    if not stock_price_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update fields provided",
        )

    return await stock_price_repository.update_stock_price(
        stock_price_id,
        stock_price_payload,
    )


@router.delete("/{stock_price_id}", status_code=status.HTTP_200_OK)
async def delete_price(
    stock_price_id: UUID,
    db: AsyncSession = Depends(async_get_db),
) -> dict:
    stock_price_repository = StockPriceRepository(db)
    deleted = await stock_price_repository.delete_stock_price(stock_price_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return {"message": "Stock data deleted successfully"}
