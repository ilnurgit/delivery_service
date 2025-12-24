from fastapi import Depends
from redis.asyncio import Redis

from delivery.core.di.redis import get_redis
from delivery.fx.cache import FxRateCache
from delivery.fx.provider_cbr import CbrXmlDailyProvider
from delivery.fx.service import FxService


def get_fx_cache(redis: Redis = Depends(get_redis)) -> FxRateCache:
    return FxRateCache(redis=redis, ttl_seconds=300)


def get_fx_service(cache: FxRateCache = Depends(get_fx_cache)) -> FxService:
    provider = CbrXmlDailyProvider()
    return FxService(cache=cache, provider=provider)
