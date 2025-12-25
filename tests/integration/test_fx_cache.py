import os
import uuid
from decimal import Decimal

import pytest
from redis.asyncio import Redis

from delivery.core.di.fx import get_fx_service
from delivery.fx.cache import FxRateCache
from delivery.fx.service import FxService

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


class CountingFxProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def get_rate(self, base: str, quote: str) -> Decimal:
        self.calls += 1
        return Decimal("96.12")


async def test_fx_rate_is_cached_in_redis(app, client):
    provider = CountingFxProvider()

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    try:
        cache = FxRateCache(redis=redis, ttl_seconds=300)
        app.dependency_overrides[get_fx_service] = lambda: FxService(cache=cache, provider=provider)

        await client.get("/health")

        code = f"DOC_{uuid.uuid4().hex[:8]}"
        r = await client.post(
            "/api/v1/parcel-types/",
            json={
                "code": code,
                "name": "Documents",
                "base_price_usd": "5.00",
                "price_per_kg_usd": "2.50",
            },
        )
        assert r.status_code == 201, r.text

        r1 = await client.post(
            "/api/v1/pricing/calculate",
            json={"parcel_type_code": code, "weight_kg": 2, "currency": "RUB"},
        )
        assert r1.status_code == 200, r1.text

        r2 = await client.post(
            "/api/v1/pricing/calculate",
            json={"parcel_type_code": code, "weight_kg": 2, "currency": "RUB"},
        )
        assert r2.status_code == 200, r2.text

        assert provider.calls == 1
        assert r1.json() == r2.json()
    finally:
        await redis.aclose()
