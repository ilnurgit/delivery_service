from delivery.parcels.repositories.memory import InMemoryParcelRepository
from delivery.parcels.services.service import ParcelService

_repo = InMemoryParcelRepository()


def get_parcel_service() -> ParcelService:
    return ParcelService(repo=_repo)
