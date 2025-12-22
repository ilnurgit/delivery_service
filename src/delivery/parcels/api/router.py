from fastapi import APIRouter, Depends

from delivery.core.di.parcels import get_parcel_service
from delivery.parcels.api.mappers import to_parcel_out, to_parcel_out_list
from delivery.parcels.api.schemas import ParcelCreate, ParcelOut
from delivery.parcels.services.service import ParcelService

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.get("/", response_model=list[ParcelOut])
async def list_parcels(service: ParcelService = Depends(get_parcel_service)) -> list[ParcelOut]:
    items = await service.list_parcels()
    return to_parcel_out_list(items)


@router.post("/", response_model=ParcelOut, status_code=201)
async def create_parcel(
    payload: ParcelCreate,
    service: ParcelService = Depends(get_parcel_service),
) -> ParcelOut:
    parcel = await service.create_parcel(
        parcel_type_code=payload.parcel_type_code,
        weight_kg=payload.weight_kg,
    )
    return to_parcel_out(parcel)
