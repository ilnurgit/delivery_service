import uuid

import pytest

pytestmark = pytest.mark.integration


async def test_create_parcel_unknown_parcel_type_returns_domain_error(client):
    await client.get("/health")

    code = f"NOPE_{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/parcels/",
        json={"title": "X", "parcel_type_code": code, "weight_kg": 1, "content_usd": "10.00"},
    )

    assert r.status_code == 404, r.text
    body = r.json()
    assert body["error"]["code"] == "parcel_type_not_found"
    assert body["error"]["details"]["code"] == code
    assert body["error"]["trace_id"] is not None


async def test_get_parcel_invalid_uuid_in_path_returns_422(client):
    await client.get("/health")

    r = await client.get("/api/v1/parcels/not-a-uuid")
    assert r.status_code == 422, r.text
    body = r.json()
    assert body["error"]["code"] == "validation_error"
