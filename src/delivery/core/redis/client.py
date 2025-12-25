from __future__ import annotations

from redis.asyncio import Redis

from delivery.core.settings import settings


def create_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)
