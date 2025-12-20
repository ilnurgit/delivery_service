import uuid

from delivery.parcels.domain.entities import Parcel
from delivery.parcels.repositories.memory import ParcelRepository


class ParcelService:
    def __init__(self, repo: ParcelRepository) -> None:
        self._repo = repo

    async def list_parcels(self) -> list[Parcel]:
        return await self._repo.list_all()

    async def create_parcel(self, parcel_type_id: str, weight_kg: float) -> Parcel:
        parcel = Parcel(
            id=str(uuid.uuid4()),
            parcel_type_id=parcel_type_id,
            weight_kg=weight_kg,
        )
        return await self._repo.create(parcel)
