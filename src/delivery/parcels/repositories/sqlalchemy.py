import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.parcel_types.db.models import ParcelTypeModel
from delivery.parcels.db.models import ParcelModel
from delivery.parcels.domain.entities import Parcel


class SqlAlchemyParcelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, parcel: Parcel) -> Parcel:
        model = ParcelModel(
            id=uuid.UUID(parcel.id),
            session_id=parcel.session_id,
            parcel_type_id=uuid.UUID(parcel.parcel_type_id),
            title=parcel.title,
            weight_kg=parcel.weight_kg,
            content_usd=Decimal(parcel.content_usd),
            delivery_cost_rub=Decimal(parcel.delivery_cost_rub)
            if parcel.delivery_cost_rub
            else None,
        )
        self._session.add(model)
        await self._session.flush()
        return parcel

    async def get_by_id_for_session(self, parcel_id: str, session_id: str) -> Parcel | None:
        stmt = (
            select(ParcelModel, ParcelTypeModel)
            .join(ParcelTypeModel, ParcelModel.parcel_type_id == ParcelTypeModel.id)
            .where(
                ParcelModel.id == uuid.UUID(parcel_id),
                ParcelModel.session_id == session_id,
            )
        )
        res = await self._session.execute(stmt)
        row = res.one_or_none()
        if row is None:
            return None

        parcel_row, pt_row = row
        return Parcel(
            id=str(parcel_row.id),
            session_id=parcel_row.session_id,
            parcel_type_id=str(parcel_row.parcel_type_id),
            parcel_type_code=pt_row.code,
            parcel_type_name=pt_row.name,
            title=parcel_row.title,
            weight_kg=parcel_row.weight_kg,
            content_usd=str(parcel_row.content_usd),
            delivery_cost_rub=str(parcel_row.delivery_cost_rub)
            if parcel_row.delivery_cost_rub is not None
            else None,
        )

    async def list_for_session(
        self,
        session_id: str,
        *,
        limit: int,
        offset: int,
        parcel_type_code: str | None = None,
        has_cost: bool | None = None,
    ) -> list[Parcel]:
        stmt = (
            select(ParcelModel, ParcelTypeModel)
            .join(ParcelTypeModel, ParcelModel.parcel_type_id == ParcelTypeModel.id)
            .where(ParcelModel.session_id == session_id)
        )

        if parcel_type_code is not None:
            stmt = stmt.where(ParcelTypeModel.code == parcel_type_code)

        if has_cost is True:
            stmt = stmt.where(ParcelModel.delivery_cost_rub.is_not(None))
        elif has_cost is False:
            stmt = stmt.where(ParcelModel.delivery_cost_rub.is_(None))

        stmt = stmt.limit(limit).offset(offset)

        res = await self._session.execute(stmt)
        rows = res.all()

        out: list[Parcel] = []
        for parcel_row, pt_row in rows:
            out.append(
                Parcel(
                    id=str(parcel_row.id),
                    session_id=parcel_row.session_id,
                    parcel_type_id=str(parcel_row.parcel_type_id),
                    parcel_type_code=pt_row.code,
                    parcel_type_name=pt_row.name,
                    title=parcel_row.title,
                    weight_kg=parcel_row.weight_kg,
                    content_usd=str(parcel_row.content_usd),
                    delivery_cost_rub=str(parcel_row.delivery_cost_rub)
                    if parcel_row.delivery_cost_rub is not None
                    else None,
                )
            )
        return out
