from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from delivery.parcel_types.domain.entities import ParcelType
from delivery.parcel_types.repositories.base import ParcelTypeRepository

pytestmark = pytest.mark.unit


@dataclass(slots=True)
class FakeParcelTypeRepo(ParcelTypeRepository):
    existing: dict[str, ParcelType] | None = None

    _existing: dict[str, ParcelType] = field(init=False)
    create_calls: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._existing = dict(self.existing or {})

    async def get_by_code(self, code: str) -> ParcelType | None:
        return self._existing.get(code)

    async def list_all(self) -> list[ParcelType]:
        return list(self._existing.values())

    async def create(
        self, *, code: str, name: str, base_price_usd: str, price_per_kg_usd: str
    ) -> ParcelType:
        self.create_calls.append(
            dict(
                code=code,
                name=name,
                base_price_usd=base_price_usd,
                price_per_kg_usd=price_per_kg_usd,
            )
        )
        pt = ParcelType(
            id="pt-new",
            code=code,
            name=name,
            base_price_usd=base_price_usd,
            price_per_kg_usd=price_per_kg_usd,
        )
        self._existing[code] = pt
        return pt
