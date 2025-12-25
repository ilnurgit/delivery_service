import pytest

pytestmark = pytest.mark.e2e


async def test_health_sets_session_cookie(client):
    r = await client.get("/health")
    assert r.status_code == 200

    # Проверка: сервер выставил Set-Cookie
    assert "set-cookie" in r.headers

    # Проверка: cookie реально попало в cookie jar клиента
    assert client.cookies.get("delivery_session_id") is not None
