import uuid

from delivery.parcel_types.domain.errors import ParcelTypeNotFoundError
from delivery.parcel_types.repositories.base import ParcelTypeRepository
from delivery.parcels.domain.entities import Parcel
from delivery.parcels.domain.errors import ParcelWeightMustBePositiveError
from delivery.parcels.repositories.memory import ParcelRepository


class ParcelService:
    def __init__(self, repo: ParcelRepository, type_repo: ParcelTypeRepository) -> None:
        self._repo = repo
        self._type_repo = type_repo

    async def list_parcels(self) -> list[Parcel]:
        return await self._repo.list_all()

    async def create_parcel(self, parcel_type_code: str, weight_kg: float) -> Parcel:
        if weight_kg <= 0:
            raise ParcelWeightMustBePositiveError(weight_kg)

        pt = await self._type_repo.get_by_code(parcel_type_code)
        if pt is None:
            raise ParcelTypeNotFoundError(parcel_type_code)

        parcel = Parcel(
            id=str(uuid.uuid4()),
            parcel_type_id=pt.id,
            weight_kg=weight_kg,
        )

        return await self._repo.create(parcel)
