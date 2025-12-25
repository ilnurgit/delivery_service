from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.parcel_types.db.models import ParcelTypeModel
from delivery.parcel_types.domain.entities import ParcelType
from delivery.parcel_types.domain.errors import ParcelTypeAlreadyExistsError
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
            base_price_usd=str(row.base_price_usd),
            price_per_kg_usd=str(row.price_per_kg_usd),
        )

    async def list_all(self) -> list[ParcelType]:
        result = await self._session.execute(select(ParcelTypeModel).order_by(ParcelTypeModel.code))
        rows = result.scalars().all()
        return [
            ParcelType(
                id=str(r.id),
                code=r.code,
                name=r.name,
                base_price_usd=str(r.base_price_usd),
                price_per_kg_usd=str(r.price_per_kg_usd),
            )
            for r in rows
        ]

    async def create(
        self, code: str, name: str, base_price_usd: str, price_per_kg_usd: str
    ) -> ParcelType:
        model = ParcelTypeModel(
            code=code,
            name=name,
            base_price_usd=Decimal(base_price_usd),
            price_per_kg_usd=Decimal(price_per_kg_usd),
        )
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as e:
            # важно: сбрасываем failed-транзакцию
            await self._session.rollback()

            msg = str(getattr(e, "orig", e))
            # самый простой и рабочий детектор под твой constraint:
            if "ix_parcel_types_code" in msg or "Key (code)" in msg:
                raise ParcelTypeAlreadyExistsError(code) from e
            raise

        return ParcelType(
            id=str(model.id),
            code=model.code,
            name=model.name,
            base_price_usd=str(model.base_price_usd),
            price_per_kg_usd=str(model.price_per_kg_usd),
        )
