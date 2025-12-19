from fastapi import APIRouter

from delivery.parcels.api.schemas import ParcelCreate, ParcelOut

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.get("/", response_model=list[ParcelOut])
async def list_parcels() -> list[ParcelOut]:
    return []


@router.post("/", response_model=ParcelOut, status_code=201)
async def create_parcel(payload: ParcelCreate) -> ParcelOut:
    return ParcelOut(id="stub", parcel_type_id=payload.parcel_type_id, weight_kg=payload.weight_kg)
