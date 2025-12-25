import uuid

import pytest

pytestmark = pytest.mark.e2e


async def test_create_and_get_parcel_in_same_session(client):
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
    assert created.status_code == 201
    parcel_id = created.json()["id"]

    got = await client.get(f"/api/v1/parcels/{parcel_id}")
    assert got.status_code == 200
    data = got.json()
    assert data["id"] == parcel_id
    assert data["parcel_type_code"] == code
    assert data["parcel_type_name"] == "Documents"
    assert data["delivery_cost_rub"] is None
