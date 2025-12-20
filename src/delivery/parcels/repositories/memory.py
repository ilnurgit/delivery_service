from typing import Protocol

from delivery.parcels.domain.entities import Parcel


class ParcelRepository(Protocol):
    async def list_all(self) -> list[Parcel]: ...

    async def create(self, parcel: Parcel) -> Parcel: ...


class InMemoryParcelRepository:
    def __init__(self) -> None:
        self._items: list[Parcel] = []

    async def list_all(self) -> list[Parcel]:
        return list(self._items)

    async def create(self, parcel: Parcel) -> Parcel:
        self._items.append(parcel)
        return parcel
