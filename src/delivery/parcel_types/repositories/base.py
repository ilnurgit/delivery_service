from __future__ import annotations

from typing import Protocol

from delivery.parcel_types.domain.entities import ParcelType


class ParcelTypeRepository(Protocol):
    async def get_by_code(self, code: str) -> ParcelType | None: ...
