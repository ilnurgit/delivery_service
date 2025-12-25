import asyncio
import uuid

import pytest

pytestmark = pytest.mark.integration


async def test_create_parcel_type_race_one_wins_other_gets_409(client):
    await client.get("/health")

    code = f"DOC_{uuid.uuid4().hex[:8]}"
    payload = {
        "code": code,
        "name": "Documents",
        "base_price_usd": "5.00",
        "price_per_kg_usd": "2.50",
    }

    r1, r2 = await asyncio.gather(
        client.post("/api/v1/parcel-types/", json=payload),
        client.post("/api/v1/parcel-types/", json=payload),
    )

    codes = sorted([r1.status_code, r2.status_code])
    assert codes == [201, 409], (r1.status_code, r1.text, r2.status_code, r2.text)

    loser = r1 if r1.status_code == 409 else r2
    body = loser.json()
    assert body["error"]["code"] == "parcel_type_already_exists"
    assert body["error"]["details"]["code"] == code
