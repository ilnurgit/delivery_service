from __future__ import annotations

from celery import Celery

from delivery.core.settings import settings

celery_app = Celery(
    "delivery",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

celery_app.autodiscover_tasks(["delivery.fx"])
