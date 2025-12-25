import uuid

import pytest

pytestmark = pytest.mark.e2e


async def test_validation_error_envelope(client):
    await client.get("/health")

    r = await client.post("/api/v1/parcels/", json={"parcel_type_code": "DOC", "weight_kg": -1})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"


async def test_domain_error_weight_must_be_positive(client):
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

    r = await client.post(
        "/api/v1/parcels/",
        json={"title": "X", "parcel_type_code": code, "weight_kg": 0, "content_usd": "10.00"},
    )
    assert r.status_code == 422
