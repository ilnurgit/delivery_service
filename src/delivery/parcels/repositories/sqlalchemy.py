import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.parcels.db.models import ParcelModel
from delivery.parcels.domain.entities import Parcel
from delivery.parcels.repositories.memory import ParcelRepository


class SqlAlchemyParcelRepository(ParcelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[Parcel]:
        result = await self._session.execute(select(ParcelModel))
        rows = result.scalars().all()

        return [
            Parcel(
                id=str(row.id),
                parcel_type_id=str(row.parcel_type_id),
                weight_kg=row.weight_kg,
            )
            for row in rows
        ]

    async def create(self, parcel: Parcel) -> Parcel:
        model = ParcelModel(
            id=uuid.UUID(parcel.id),
            parcel_type_id=parcel.parcel_type_id,
            weight_kg=parcel.weight_kg,
        )

        self._session.add(model)
        await self._session.commit()

        return parcel
