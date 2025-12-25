import asyncio
from decimal import Decimal

from redis.asyncio import Redis

from delivery.core.celery_app import celery_app
from delivery.core.settings import settings
from delivery.fx.cache import FxRateCache
from delivery.fx.provider_cbr import CbrXmlDailyProvider


async def _refresh() -> str:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        cache = FxRateCache(redis=redis, ttl_seconds=60 * 60)
        provider = CbrXmlDailyProvider()

        rate: Decimal = await provider.get_rate("USD", "RUB")
        await cache.set_rate("USD", "RUB", rate)
        return "ok"
    finally:
        await redis.aclose()


@celery_app.task(name="fx.refresh_usd_rub")
def refresh_usd_rub() -> str:
    return asyncio.run(_refresh())
