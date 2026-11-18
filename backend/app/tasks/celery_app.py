
from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "brandguard",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.document_tasks",
        "app.tasks.review_tasks",
        "app.tasks.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    broker_connection_retry_on_startup=True,

    task_routes={
        "brandguard.documents.*": {"queue": "documents"},
        "brandguard.reviews.*": {"queue": "reviews"},
        "brandguard.notifications.*": {"queue": "notifications"},
    },

    result_expires=3600,
)

celery_app.autodiscover_tasks(
    ["app.tasks"],
    force=True,
)
