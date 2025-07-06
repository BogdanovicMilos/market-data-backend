from celery import Celery

from application.config.settings import settings


celery = Celery(
    "fastapi_ingest",
    broker=settings.redis_broker,
    backend=settings.redis_backend,
    include=["application.celery.tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
)
