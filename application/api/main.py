from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application.api.routers import stock_ingestion, stock_price
from application.config.settings import settings


VERSION = "0.1.0"


app = FastAPI(
    title="Stock Market API",
    version=VERSION,
)


origins = settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stock_price.router)
app.include_router(stock_ingestion.router)


@app.get("/healthcheck", operation_id="health_check")
async def health_check():
    return {"message": "Ok"}
