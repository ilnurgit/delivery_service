from __future__ import annotations

from celery import Celery

from delivery.core.db import models  # noqa: F401
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

celery_app.autodiscover_tasks(["delivery.fx", "delivery.parcels"])
# ---- Beat schedule ----
celery_app.conf.beat_schedule = {
    "refresh-usd-rub-every-1-minute": {
        "task": "fx.refresh_usd_rub",
        "schedule": 60.0,
    },
    "refresh-parcels-delivery-costs-every-5-minutes": {
        "task": "parcels.refresh_delivery_costs",
        "schedule": 300.0,
        "args": (500,),
    },
}
