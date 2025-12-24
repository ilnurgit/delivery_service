from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from delivery.core.db.session import get_session as prod_get_session
from delivery.main import create_app

ROOT = Path(__file__).resolve().parents[1]


def _load_env_test() -> None:
    env_path = ROOT / ".env.test"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        k, v = stripped.split("=", 1)
        os.environ[k.strip()] = v.strip()


@pytest.fixture(scope="session", autouse=True)
def _load_env_and_migrate() -> None:
    _load_env_test()
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)


@pytest.fixture
async def engine() -> AsyncEngine:
    db_url = os.environ["DATABASE_URL"]
    eng = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def _clean_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.exec_driver_sql("TRUNCATE parcels, parcel_types RESTART IDENTITY CASCADE;")
    yield


@pytest.fixture
def app(session_factory: async_sessionmaker[AsyncSession]):
    app_ = create_app()

    async def test_get_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app_.dependency_overrides[prod_get_session] = test_get_session
    return app_


@pytest.fixture
async def client(app) -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
