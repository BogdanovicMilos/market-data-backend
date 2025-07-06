from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from application.config.settings import settings


ASYNC_SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@"
    f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}"
)


SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}@"
    f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_database}"
)

_session_maker = None


def async_session_maker():
    global _session_maker
    if _session_maker is None:
        async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL)
        _session_maker = sessionmaker(
            bind=async_engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_maker


def session_maker():
    global _session_maker
    if _session_maker is None:
        engine = create_engine(SYNC_DATABASE_URL, connect_args=connect_args())
        _session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    return _session_maker


def use_ssl():
    return settings.ssl_enabled == "True"


def connect_args():
    return {"sslmode": "require"} if use_ssl() else {}
