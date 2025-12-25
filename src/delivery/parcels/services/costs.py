from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from delivery.core.db.session import async_session_factory
from delivery.parcels.db.models import ParcelModel


class ParcelCostRefresher:
    def __init__(
        self, fx, session_factory: async_sessionmaker[AsyncSession] = async_session_factory
    ):
        self._fx = fx
        self._session_factory = session_factory

    async def refresh_unprocessed(
        self,
        *,
        batch_size: int,
        session: AsyncSession | None = None,
    ) -> int:
        if session is not None:
            return await self._refresh(session, batch_size=batch_size)

        async with self._session_factory() as s:
            updated = await self._refresh(s, batch_size=batch_size)
            await s.commit()
            return updated

    async def _refresh(self, session: AsyncSession, *, batch_size: int) -> int:
        rate: Decimal = await self._fx.get_rate("USD", "RUB")

        stmt = (
            select(ParcelModel)
            .where(ParcelModel.delivery_cost_rub.is_(None))
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        res = await session.execute(stmt)
        rows = list(res.scalars().all())

        if not rows:
            return 0

        updated = 0
        for p in rows:
            weight = Decimal(str(p.weight_kg))
            content = Decimal(str(p.content_usd))

            usd_cost = (weight * Decimal("0.5") + content * Decimal("0.01")).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            rub_cost = (usd_cost * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            p.delivery_cost_rub = rub_cost
            updated += 1

        await session.flush()
        return updated
