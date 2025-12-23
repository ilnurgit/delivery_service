from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from delivery.core.money import Money
from delivery.core.money_ops import convert
from delivery.fx.service import FxService
from delivery.parcel_types.domain.errors import ParcelTypeNotFoundError
from delivery.parcel_types.repositories.base import ParcelTypeRepository


class CostCalculator:
    def __init__(self, type_repo: ParcelTypeRepository, fx: FxService) -> None:
        self._type_repo = type_repo
        self._fx = fx

    async def calculate(self, parcel_type_code: str, weight_kg: float, currency: str) -> Money:
        pt = await self._type_repo.get_by_code(parcel_type_code)
        if pt is None:
            raise ParcelTypeNotFoundError(parcel_type_code)

        base = Decimal(pt.base_price_usd)
        per_kg = Decimal(pt.price_per_kg_usd)
        weight = Decimal(str(weight_kg))

        amount_usd = (base + (per_kg * weight)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        money_usd = Money(amount=amount_usd, currency="USD")

        if currency == "USD":
            return money_usd

        if currency == "RUB":
            rate = await self._fx.get_rate("USD", "RUB")
            return convert(money_usd, rate=rate, target_currency="RUB")

        raise ValueError(f"Unsupported currency: {currency}")
