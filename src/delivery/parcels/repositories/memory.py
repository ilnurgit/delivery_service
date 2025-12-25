from __future__ import annotations

from typing import Protocol

from delivery.parcels.domain.entities import Parcel


class ParcelRepository(Protocol):
    async def create(self, parcel: Parcel) -> Parcel: ...

    async def get_by_id_for_session(self, parcel_id: str, session_id: str) -> Parcel | None: ...

    async def list_for_session(
        self,
        session_id: str,
        *,
        limit: int,
        offset: int,
        parcel_type_code: str | None = None,
        has_cost: bool | None = None,
    ) -> list[Parcel]: ...


class InMemoryParcelRepository:
    def __init__(self) -> None:
        self._items: list[Parcel] = []

    async def create(self, parcel: Parcel) -> Parcel:
        self._items.append(parcel)
        return parcel

    async def get_by_id_for_session(self, parcel_id: str, session_id: str) -> Parcel | None:
        for p in self._items:
            if p.id == parcel_id and p.session_id == session_id:
                return p
        return None

    async def list_for_session(
        self,
        session_id: str,
        *,
        limit: int,
        offset: int,
        parcel_type_code: str | None = None,
        has_cost: bool | None = None,
    ) -> list[Parcel]:
        items = [p for p in self._items if p.session_id == session_id]

        if parcel_type_code is not None:
            items = [p for p in items if p.parcel_type_code == parcel_type_code]

        if has_cost is True:
            items = [p for p in items if p.delivery_cost_rub is not None]
        elif has_cost is False:
            items = [p for p in items if p.delivery_cost_rub is None]

        return items[offset : offset + limit]
