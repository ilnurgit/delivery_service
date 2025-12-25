import uuid

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.e2e


async def test_parcel_is_not_visible_for_another_session(app, client):
    # client = A
    await client.get("/health")

    code = f"DOC_{uuid.uuid4().hex[:8]}"
    await client.post(
        "/api/v1/parcel-types/",
        json={
            "code": code,
            "name": "Documents",
            "base_price_usd": "5.00",
            "price_per_kg_usd": "2.50",
        },
    )

    created = await client.post(
        "/api/v1/parcels/",
        json={
            "title": "Passport",
            "parcel_type_code": code,
            "weight_kg": 2,
            "content_usd": "100.00",
        },
    )
    parcel_id = created.json()["id"]

    # client B (новая cookie jar => новая сессия)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client_b:
        await client_b.get("/health")
        r = await client_b.get(f"/api/v1/parcels/{parcel_id}")
        assert r.status_code == 404
