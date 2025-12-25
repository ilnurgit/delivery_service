from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from delivery.core.di.parcels import get_parcel_service
from delivery.core.di.session import get_session_id
from delivery.parcels.api.mappers import to_parcel_out, to_parcel_out_list
from delivery.parcels.api.schemas import ParcelCreate, ParcelOut
from delivery.parcels.domain.errors import ParcelNotFoundError
from delivery.parcels.services.service import ParcelService

router = APIRouter(prefix="/parcels", tags=["parcels"])


@router.get("/", response_model=list[ParcelOut])
async def list_parcels(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    parcel_type_code: str | None = Query(default=None),
    has_cost: bool | None = None,
    service: ParcelService = Depends(get_parcel_service),
) -> list[ParcelOut]:
    session_id = request.state.session_id
    items = await service.list_parcels(
        session_id=session_id,
        limit=limit,
        offset=offset,
        parcel_type_code=parcel_type_code,
        has_cost=has_cost,
    )
    return to_parcel_out_list(items)


@router.get("/{parcel_id}", response_model=ParcelOut)
async def get_parcel(
    parcel_id: UUID,
    service: ParcelService = Depends(get_parcel_service),
    session_id: str = Depends(get_session_id),
) -> ParcelOut:
    parcel = await service.get_parcel(parcel_id=str(parcel_id), session_id=session_id)
    if parcel is None:
        raise ParcelNotFoundError(str(parcel_id))
    return to_parcel_out(parcel)


@router.post("/", response_model=ParcelOut, status_code=201)
async def create_parcel(
    payload: ParcelCreate,
    service: ParcelService = Depends(get_parcel_service),
    session_id: str = Depends(get_session_id),
) -> ParcelOut:
    parcel = await service.create_parcel(
        session_id=session_id,
        parcel_type_code=payload.parcel_type_code,
        title=payload.title,
        weight_kg=payload.weight_kg,
        content_usd=payload.content_usd,
    )
    return to_parcel_out(parcel)
