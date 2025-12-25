from __future__ import annotations

from fastapi import APIRouter, Query

from delivery.core.celery_app import celery_app

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.post("/refresh-costs")
async def refresh_costs(
    batch_size: int = Query(default=500, ge=1, le=5000),
) -> dict[str, str | int]:
    celery_app.send_task("parcels.refresh_delivery_costs", args=(batch_size,))
    return {"status": "queued", "batch_size": batch_size}
