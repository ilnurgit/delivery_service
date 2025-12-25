from __future__ import annotations

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

    async def create_parcel(
        self,
        *,
        session_id: str,
        parcel_type_code: str,
        title: str,
        weight_kg: float,
        content_usd: str,
    ) -> Parcel:
        if weight_kg <= 0:
            raise ParcelWeightMustBePositiveError(weight_kg)

        pt = await self._type_repo.get_by_code(parcel_type_code)
        if pt is None:
            raise ParcelTypeNotFoundError(parcel_type_code)

        parcel = Parcel(
            id=str(uuid.uuid4()),
            session_id=session_id,
            parcel_type_id=pt.id,
            parcel_type_code=pt.code,
            parcel_type_name=pt.name,
            title=title,
            weight_kg=weight_kg,
            content_usd=content_usd,
            delivery_cost_rub=None,
        )
        return await self._repo.create(parcel)

    async def get_parcel(self, *, parcel_id: str, session_id: str) -> Parcel | None:
        return await self._repo.get_by_id_for_session(parcel_id, session_id)

    async def list_parcels(
        self,
        *,
        session_id: str,
        limit: int,
        offset: int,
        parcel_type_code: str | None,
        has_cost: bool | None,
    ) -> list[Parcel]:
        return await self._repo.list_for_session(
            session_id,
            limit=limit,
            offset=offset,
            parcel_type_code=parcel_type_code,
            has_cost=has_cost,
        )
