from __future__ import annotations


async def test_pricing_usd_and_rub(client):
    r = await client.post(
        "/api/v1/parcel-types/",
        json={
            "code": "DOC",
            "name": "Documents",
            "base_price_usd": "5.00",
            "price_per_kg_usd": "2.50",
        },
    )
    assert r.status_code == 201, r.text

    # USD
    r = await client.post(
        "/api/v1/pricing/calculate",
        json={"parcel_type_code": "DOC", "weight_kg": 2, "currency": "USD"},
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"amount": "10.00", "currency": "USD"}

    # RUB
    r = await client.post(
        "/api/v1/pricing/calculate",
        json={"parcel_type_code": "DOC", "weight_kg": 2, "currency": "RUB"},
    )
    assert r.status_code == 200, r.text
    assert r.json() == {"amount": "961.20", "currency": "RUB"}
