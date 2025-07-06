from __future__ import annotations

import logging
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from starlette import status

from application.api.dependencies.middleware import token_auth_middleware
from application.celery.tasks import process_stocks_data_task
from domain.stock_data.stock_data_ingestion import BatchDataProcessor
from load_symbols import load_symbols


router = APIRouter(
    prefix="/api",
    tags=["Ingestion"],
    dependencies=[Depends(token_auth_middleware)],
)

log = logging.getLogger("stock_ingestion")

cfg = load_symbols()
SYMBOLS: list[str] = cfg.get("symbols", ["AAPL", "MSFT"])


@router.post("/ingestion", status_code=status.HTTP_200_OK)
async def ingest_stock_data(background_tasks: BackgroundTasks):
    processor = BatchDataProcessor()

    async def run():
        log.info("Starting on-demand ETL via API")
        await processor.run_batch(SYMBOLS)
        log.info("Finished on-demand ETL via API")

    background_tasks.add_task(run)
    return {"message": "ETL process started in background"}


@router.post("/stocks-data", status_code=status.HTTP_202_ACCEPTED)
async def ingest_stocks_data_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type: please upload a CSV file.",
        )

    raw = await file.read()
    csv_string = raw.decode("utf-8")

    # Enqueue background job
    process_stocks_data_task.delay(csv_string)

    return {"message": "Processing enqueued"}
