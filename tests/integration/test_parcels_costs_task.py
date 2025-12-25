import uuid
from decimal import Decimal

import pytest

from delivery.parcels.tasks import _run_refresh

pytestmark = pytest.mark.integration


class FakeFxService:
    async def get_rate(self, base: str, quote: str) -> Decimal:
        return Decimal("96.12")


async def test_refresh_costs_sets_delivery_cost_rub(app, client, session_factory):
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
    assert r.status_code == 201

    r = await client.post(
        "/api/v1/parcels/",
        json={"title": "X", "parcel_type_code": code, "weight_kg": 2, "content_usd": "100.00"},
    )
    assert r.status_code == 201
    pid = r.json()["id"]

    got = await client.get(f"/api/v1/parcels/{pid}")
    assert got.status_code == 200
    assert got.json()["delivery_cost_rub"] is None

    async with session_factory() as s:
        updated = await _run_refresh(batch_size=50, session=s, fx=FakeFxService())
        await s.commit()
    assert updated >= 1

    # ожидаемая формула:
    # (weight*0.5 + content*0.01) * rate
    # (2*0.5 + 100*0.01) = (1 + 1) = 2 USD
    # rate = 96.12 => 192.24 RUB
    got2 = await client.get(f"/api/v1/parcels/{pid}")
    assert got2.status_code == 200
    assert got2.json()["delivery_cost_rub"] == "192.24"
