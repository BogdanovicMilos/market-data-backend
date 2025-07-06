from celery import Celery


# Docker configuration
broker = "redis://redis:6379/0"
backend = "redis://redis:6379/1"

# Local configuration
# broker = "redis://localhost:6379/0"
# backend = "redis://localhost:6379/1"

celery = Celery(
    "fastapi_ingest",
    broker=broker,
    backend=backend,
    include=["application.celery.tasks"],
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
)
