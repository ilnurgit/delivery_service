from __future__ import annotations

from fastapi import APIRouter

from delivery.fx.tasks import refresh_usd_rub

router = APIRouter(prefix="/fx", tags=["fx"])


@router.post("/refresh")
async def refresh_rate() -> dict[str, str]:
    refresh_usd_rub.delay()
    return {"status": "queued"}
