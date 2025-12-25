import uuid

import pytest

pytestmark = pytest.mark.integration


async def test_list_parcels_pagination(client):
    await client.get("/health")

    code = f"DOC_{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/parcel-types/",
        json={
            "code": code,
            "name": "Documents",
            "base_price_usd": "5.00",
            "price_per_kg_usd": "2.50",
        },
    )
    assert r.status_code == 201, r.text

    created_ids: list[str] = []
    for i in range(3):
        r = await client.post(
            "/api/v1/parcels/",
            json={
                "title": f"Parcel-{i}",
                "parcel_type_code": code,
                "weight_kg": 1,
                "content_usd": "10.00",
            },
        )
        assert r.status_code == 201, r.text
        created_ids.append(r.json()["id"])

    # page 1
    r = await client.get("/api/v1/parcels/?limit=2&offset=0")
    assert r.status_code == 200, r.text
    page1 = r.json()
    assert len(page1) == 2

    # page 2
    r = await client.get("/api/v1/parcels/?limit=2&offset=2")
    assert r.status_code == 200, r.text
    page2 = r.json()
    assert len(page2) == 1

    # проверяем, что все созданные попали в объединение страниц (без требования порядка)
    got_ids = {x["id"] for x in (page1 + page2)}
    assert got_ids == set(created_ids)


async def test_list_parcels_has_cost_filter(client):
    await client.get("/health")

    code = f"DOC_{uuid.uuid4().hex[:8]}"
    r = await client.post(
        "/api/v1/parcel-types/",
        json={
            "code": code,
            "name": "Documents",
            "base_price_usd": "5.00",
            "price_per_kg_usd": "2.50",
        },
    )
    assert r.status_code == 201, r.text

    r = await client.post(
        "/api/v1/parcels/",
        json={"title": "X", "parcel_type_code": code, "weight_kg": 1, "content_usd": "10.00"},
    )
    assert r.status_code == 201, r.text

    # пока delivery_cost_rub не проставляется — has_cost=true должен дать пусто
    r = await client.get("/api/v1/parcels/?has_cost=true")
    assert r.status_code == 200, r.text
    assert r.json() == []

    # has_cost=false должен вернуть хотя бы одну
    r = await client.get("/api/v1/parcels/?has_cost=false")
    assert r.status_code == 200, r.text
    assert len(r.json()) >= 1
