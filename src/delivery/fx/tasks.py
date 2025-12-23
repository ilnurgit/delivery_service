from __future__ import annotations

import asyncio
from decimal import Decimal

from delivery.core.celery_app import celery_app
from delivery.core.redis.client import create_redis
from delivery.fx.cache import FxRateCache
from delivery.fx.provider import FxRateProvider
from delivery.fx.service import FxService


async def _refresh_usd_rub() -> None:
    redis = create_redis()
    cache = FxRateCache(redis=redis, ttl_seconds=300)
    fx = FxService(cache=cache, provider=FxRateProvider())

    rate = await fx.provider.get_rate("USD", "RUB")
    await cache.set_rate("USD", "RUB", Decimal(rate))

    await redis.aclose()


@celery_app.task(name="fx.refresh_usd_rub")
def refresh_usd_rub() -> str:
    asyncio.run(_refresh_usd_rub())
    return "ok"
