import pytest

pytestmark = pytest.mark.e2e


async def test_create_parcel_type_then_conflict(client):
    await client.get("/health")

    payload = {
        "code": "DOC",
        "name": "Documents",
        "base_price_usd": "5.00",
        "price_per_kg_usd": "2.50",
    }

    r1 = await client.post("/api/v1/parcel-types/", json=payload)
    assert r1.status_code in (201, 409)
    r2 = await client.post("/api/v1/parcel-types/", json=payload)
    assert r2.status_code == 409
    body = r2.json()
    assert body["error"]["code"] == "parcel_type_already_exists"
    assert body["error"]["details"]["code"] == "DOC"
