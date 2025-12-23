from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.di.db import get_db_session
from delivery.parcel_types.api.mappers import to_out, to_out_list
from delivery.parcel_types.api.schemas import ParcelTypeCreate, ParcelTypeOut
from delivery.parcel_types.repositories.sqlalchemy import SqlAlchemyParcelTypeRepository
from delivery.parcel_types.services.service import ParcelTypeService

router = APIRouter(prefix="/parcel-types", tags=["parcel-types"])


def get_service(session: AsyncSession = Depends(get_db_session)) -> ParcelTypeService:
    return ParcelTypeService(SqlAlchemyParcelTypeRepository(session))


@router.get("/", response_model=list[ParcelTypeOut])
async def list_types(service: ParcelTypeService = Depends(get_service)) -> list[ParcelTypeOut]:
    items = await service.list_types()
    return to_out_list(items)


@router.post("/", response_model=ParcelTypeOut, status_code=status.HTTP_201_CREATED)
async def create_type(
    payload: ParcelTypeCreate,
    service: ParcelTypeService = Depends(get_service),
) -> ParcelTypeOut:
    pt = await service.create_type(
        code=payload.code,
        name=payload.name,
        base_price_usd=payload.base_price_usd,
        price_per_kg_usd=payload.price_per_kg_usd,
    )
    return to_out(pt)


@router.get("/{code}", response_model=ParcelTypeOut)
async def get_type(code: str, service: ParcelTypeService = Depends(get_service)) -> ParcelTypeOut:
    pt = await service.get_type(code=code)
    if pt is None:
        raise HTTPException(status_code=404, detail="Parcel type not found")
    return to_out(pt)
