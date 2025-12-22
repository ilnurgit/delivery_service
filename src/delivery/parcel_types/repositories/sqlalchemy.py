from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.parcel_types.db.models import ParcelTypeModel
from delivery.parcel_types.domain.entities import ParcelType
from delivery.parcel_types.repositories.base import ParcelTypeRepository


class SqlAlchemyParcelTypeRepository(ParcelTypeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_code(self, code: str) -> ParcelType | None:
        result = await self._session.execute(
            select(ParcelTypeModel).where(ParcelTypeModel.code == code)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return ParcelType(
            id=str(row.id),
            code=row.code,
            name=row.name,
        )

    async def list_all(self) -> list[ParcelType]:
        result = await self._session.execute(select(ParcelTypeModel).order_by(ParcelTypeModel.code))
        rows = result.scalars().all()
        return [
            ParcelType(
                id=str(r.id),
                code=r.code,
                name=r.name,
            )
            for r in rows
        ]

    async def create(self, code: str, name: str) -> ParcelType:
        model = ParcelTypeModel(code=code, name=name)
        self._session.add(model)
        await self._session.flush()
        return ParcelType(
            id=str(model.id),
            code=model.code,
            name=model.name,
        )
