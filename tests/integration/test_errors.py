from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


async def test_validation_error_envelope(client):
    r = await client.post(
        "/api/v1/parcels/",
        json={"parcel_type_code": "DOC", "weight_kg": -1},
    )
    assert r.status_code == 422
    body = r.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["trace_id"] is not None


async def test_not_found_envelope(client):
    r = await client.get("/this-does-not-exist")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body
    assert body["error"]["code"] == "http_error"
    assert body["error"]["trace_id"] is not None
