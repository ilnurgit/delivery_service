from __future__ import annotations

import asyncio
import os
import subprocess
from collections.abc import AsyncIterator
from decimal import Decimal
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.e2e


def _load_env_test() -> None:
    env_path = ROOT / ".env.test"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        k, v = stripped.split("=", 1)
        k = k.strip()
        v = v.strip()

        os.environ.setdefault(k, v)


_load_env_test()

from delivery.core.db.session import get_session as prod_get_session  # noqa: E402
from delivery.core.di.fx import get_fx_service  # noqa: E402
from delivery.main import create_app  # noqa: E402


class FakeFxService:
    async def get_rate(self, base: str, quote: str) -> Decimal:
        return Decimal("96.12")


@pytest.fixture(autouse=True)
async def _flush_redis():
    r = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    await r.flushall()
    try:
        yield
    finally:
        await r.flushall()
        await r.aclose()


async def _truncate_tables() -> None:
    db_url = os.environ["DATABASE_URL"]
    eng = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    try:
        async with eng.begin() as conn:
            await conn.execute(
                text("TRUNCATE TABLE parcel_types, parcels RESTART IDENTITY CASCADE;")
            )
    finally:
        await eng.dispose()


@pytest.fixture(scope="session", autouse=True)
def _migrate() -> None:
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
    asyncio.run(_truncate_tables())


@pytest.fixture(scope="session")
async def engine() -> AsyncEngine:
    db_url = os.environ["DATABASE_URL"]
    eng = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture(autouse=True)
async def db_connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            yield conn
        finally:
            if trans.is_active:
                await trans.rollback()


@pytest.fixture
def session_factory(db_connection) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=db_connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def app(session_factory: async_sessionmaker[AsyncSession]):
    app_ = create_app()

    async def test_get_session():
        async with session_factory() as session:
            yield session

    app_.dependency_overrides[prod_get_session] = test_get_session

    fake_fx = FakeFxService()
    app_.dependency_overrides[get_fx_service] = lambda: fake_fx
    return app_


@pytest.fixture
async def client(app) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
