from __future__ import annotations

import asyncio

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.celery_app import celery_app
from delivery.core.settings import settings
from delivery.fx.cache import FxRateCache
from delivery.fx.provider_cbr import CbrXmlDailyProvider
from delivery.fx.service import FxService
from delivery.parcels.services.costs import ParcelCostRefresher


async def _run_refresh(
    *,
    batch_size: int,
    session: AsyncSession | None = None,
    fx: FxService | None = None,
) -> int:
    """
    В тестах можем передать:
      - session (транзакция тестовой БД)
      - fx (FakeFxService), чтобы не ходить во внешние API/redis

    В проде, если fx=None — создаём FxService с redis-кэшем и провайдером ЦБ.
    """
    if fx is not None:
        refresher = ParcelCostRefresher(fx=fx)
        return await refresher.refresh_unprocessed(batch_size=batch_size, session=session)

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        cache = FxRateCache(redis=redis, ttl_seconds=60 * 60)
        provider = CbrXmlDailyProvider()
        fx = FxService(cache=cache, provider=provider)

        refresher = ParcelCostRefresher(fx=fx)
        return await refresher.refresh_unprocessed(batch_size=batch_size, session=session)
    finally:
        await redis.aclose()


@celery_app.task(name="parcels.refresh_delivery_costs")
def refresh_delivery_costs(batch_size: int = 500) -> int:
    async def _run_all() -> int:
        total = 0
        while True:
            updated = await _run_refresh(batch_size=batch_size)
            if updated == 0:
                break
            total += updated
        return total

    return asyncio.run(_run_all())
