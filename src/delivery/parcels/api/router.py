from fastapi import APIRouter, Depends

from delivery.core.di.parcels import get_parcel_service
from delivery.parcels.api.schemas import ParcelCreate, ParcelOut
from delivery.parcels.services.service import ParcelService

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.get("/", response_model=list[ParcelOut])
async def list_parcels(service: ParcelService = Depends(get_parcel_service)) -> list[ParcelOut]:
    items = await service.list_parcels()
    return [
        ParcelOut(id=i.id, parcel_type_id=i.parcel_type_id, weight_kg=i.weight_kg) for i in items
    ]


@router.post("/", response_model=ParcelOut, status_code=201)
async def create_parcel(
    payload: ParcelCreate,
    service: ParcelService = Depends(get_parcel_service),
) -> ParcelOut:
    parcel = await service.create_parcel(
        parcel_type_id=payload.parcel_type_id,
        weight_kg=payload.weight_kg,
    )
    return ParcelOut(id=parcel.id, parcel_type_id=parcel.parcel_type_id, weight_kg=parcel.weight_kg)
