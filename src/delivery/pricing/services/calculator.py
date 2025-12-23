from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from delivery.core.money import Money
from delivery.parcel_types.domain.errors import ParcelTypeNotFoundError
from delivery.parcel_types.repositories.base import ParcelTypeRepository


class CostCalculator:
    def __init__(self, type_repo: ParcelTypeRepository) -> None:
        self._type_repo = type_repo

    async def calculate_usd(self, parcel_type_code: str, weight_kg: float) -> Money:
        pt = await self._type_repo.get_by_code(parcel_type_code)
        if pt is None:
            raise ParcelTypeNotFoundError(parcel_type_code)

        base = Decimal(pt.base_price_usd)
        per_kg = Decimal(pt.price_per_kg_usd)
        weight = Decimal(str(weight_kg))

        amount = (base + (per_kg * weight)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(amount=amount, currency="USD")
