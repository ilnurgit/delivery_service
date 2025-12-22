from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from delivery.core.money import Money

TARIFFS_USD: dict[str, dict[str, str]] = {
    "DOC": {"base": "5.00", "per_kg": "2.50"},
    "BOX": {"base": "10.00", "per_kg": "3.00"},
}


class TariffNotFoundError(ValueError):
    pass


class CostCalculator:
    def calculate_usd(self, parcel_type_code: str, weight_kg: float) -> Money:
        tariff = TARIFFS_USD.get(parcel_type_code)
        if tariff is None:
            raise TariffNotFoundError(parcel_type_code)

        base = Decimal(tariff["base"])
        per_kg = Decimal(tariff["per_kg"])
        weight = Decimal(str(weight_kg))

        amount = (base + (per_kg * weight)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Money(amount=amount, currency="USD")
