import asyncio
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient

from delivery.core.di.fx import get_fx_service

pytestmark = pytest.mark.integration


class CountingFxService:
    def __init__(self) -> None:
        self.calls = 0

    async def get_rate(self, base: str, quote: str) -> Decimal:
        self.calls += 1
        return Decimal("96.12")


async def test_fx_cache_ttl_expires(app):
    fx = CountingFxService()
    app.dependency_overrides[get_fx_service] = lambda: fx

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.get("/health")
        await client.post(
            "/api/v1/parcel-types/",
            json={
                "code": "DOC",
                "name": "Documents",
                "base_price_usd": "5.00",
                "price_per_kg_usd": "2.50",
            },
        )

        await client.post(
            "/api/v1/pricing/calculate",
            json={"parcel_type_code": "DOC", "weight_kg": 2, "currency": "RUB"},
        )
        assert fx.calls == 1

        await asyncio.sleep(1.1)

        await client.post(
            "/api/v1/pricing/calculate",
            json={"parcel_type_code": "DOC", "weight_kg": 2, "currency": "RUB"},
        )
        assert fx.calls == 2
