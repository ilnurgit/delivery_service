from __future__ import annotations

import asyncio

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from delivery.core.celery_app import celery_app
from delivery.core.db import models  # noqa: F401
from delivery.core.settings import settings
from delivery.fx.cache import FxRateCache
from delivery.fx.provider_cbr import CbrXmlDailyProvider
from delivery.fx.service import FxService
from delivery.parcels.services.costs import ParcelCostRefresher


async def _run_refresh(
    *, batch_size: int, session: AsyncSession, fx: FxService | None = None
) -> int:
    if fx is not None:
        return await ParcelCostRefresher(fx=fx).refresh_unprocessed(
            batch_size=batch_size,
            session=session,
        )

    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        fx = FxService(
            cache=FxRateCache(redis=redis, ttl_seconds=60 * 60),
            provider=CbrXmlDailyProvider(),
        )
        return await ParcelCostRefresher(fx=fx).refresh_unprocessed(
            batch_size=batch_size,
            session=session,
        )
    finally:
        await redis.aclose()


async def _run_all(batch_size: int) -> int:
    engine = create_async_engine(
        str(settings.database_url),
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        total = 0
        while True:
            async with session_factory() as session:
                updated = await _run_refresh(batch_size=batch_size, session=session)

            if updated == 0:
                break
            total += updated

        return total
    finally:
        await engine.dispose()


@celery_app.task(name="parcels.refresh_delivery_costs")
def refresh_delivery_costs(batch_size: int = 500) -> int:
    return asyncio.run(_run_all(batch_size))
