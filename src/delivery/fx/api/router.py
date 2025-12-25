from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from delivery.core.di.redis import get_redis
from delivery.fx.cache import FxRateCache

router = APIRouter(prefix="/fx", tags=["fx"])


def get_cache(redis: Redis = Depends(get_redis)) -> FxRateCache:
    return FxRateCache(redis=redis, ttl_seconds=300)


@router.post("/seed")
async def seed_rate(cache: FxRateCache = Depends(get_cache)) -> dict[str, str]:
    await cache.set_rate("USD", "RUB", Decimal("96.12"))
    return {"status": "ok"}


@router.get("/rate")
async def get_rate(cache: FxRateCache = Depends(get_cache)) -> dict[str, str]:
    rate = await cache.get_rate("USD", "RUB")
    return {"USD_RUB": str(rate) if rate is not None else "miss"}
