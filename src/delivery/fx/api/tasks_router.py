from __future__ import annotations

from fastapi import APIRouter

from delivery.core.celery_app import celery_app

router = APIRouter(prefix="/fx", tags=["fx"])


@router.post("/refresh")
async def refresh_rate() -> dict[str, str]:
    celery_app.send_task("fx.refresh_usd_rub")
    return {"status": "queued"}
