from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.integration


async def test_parcel_id_is_scoped_to_session(app):
    transport = ASGITransport(app=app)

    async with (
        AsyncClient(transport=transport, base_url="http://test") as a,
        AsyncClient(transport=transport, base_url="http://test") as b,
    ):
        # получаем cookie для каждой "сессии"
        await a.get("/health")
        await b.get("/health")

        # создаём тип посылки (можно через A)
        r = await a.post(
            "/api/v1/parcel-types/",
            json={
                "code": "DOC",
                "name": "Documents",
                "base_price_usd": "5.00",
                "price_per_kg_usd": "2.50",
            },
        )
        assert r.status_code == 201, r.text

        # создаём посылку в сессии A
        r = await a.post(
            "/api/v1/parcels/",
            json={
                "title": "Passport",
                "parcel_type_code": "DOC",
                "weight_kg": 2,
                "content_usd": "100.00",
            },
        )
        assert r.status_code == 201, r.text
        parcel_id = r.json()["id"]

        # A видит свою посылку
        r = await a.get(f"/api/v1/parcels/{parcel_id}")
        assert r.status_code == 200, r.text
        assert r.json()["id"] == parcel_id

        # B НЕ должен видеть посылку A
        r = await b.get(f"/api/v1/parcels/{parcel_id}")
        assert r.status_code == 404, r.text
        body = r.json()
        assert "error" in body
        assert body["error"]["code"] == "parcel_not_found"
        assert body["error"]["trace_id"] is not None
        assert body["error"]["details"]["parcel_id"] == parcel_id
