import pytest

pytestmark = pytest.mark.integration


async def test_create_parcel_type_duplicate_returns_409(client):
    payload = {
        "code": "DOC",
        "name": "Documents",
        "base_price_usd": "5.00",
        "price_per_kg_usd": "2.50",
    }

    r1 = await client.post("/api/v1/parcel-types/", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/parcel-types/", json=payload)
    assert r2.status_code == 409
    data = r2.json()
    assert data["error"]["code"] == "parcel_type_already_exists"
    assert data["error"]["details"]["code"] == "DOC"
