from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.parcels.db.models import ParcelModel


class SqlAlchemyParcelCostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_unprocessed_ids(self, *, limit: int) -> list[str]:
        stmt = (
            select(ParcelModel.id)
            .where(ParcelModel.delivery_cost_rub.is_(None))
            .order_by(ParcelModel.created_at.asc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        ids = res.scalars().all()
        return [str(x) for x in ids]

    async def set_delivery_cost_rub(self, *, parcel_id: str, cost_rub: Decimal) -> None:
        stmt = (
            update(ParcelModel)
            .where(ParcelModel.id == parcel_id)  # SQLAlchemy сам приведёт UUID
            .values(delivery_cost_rub=cost_rub)
        )
        await self._session.execute(stmt)
