from __future__ import annotations

from redis.asyncio import Redis

from delivery.core.redis.client import redis


def get_redis() -> Redis:
    return redis
