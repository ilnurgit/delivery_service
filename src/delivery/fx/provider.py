from __future__ import annotations

from decimal import Decimal


class FxRateProvider:
    async def get_rate(self, base: str, quote: str) -> Decimal:
        if (base, quote) == ("USD", "RUB"):
            return Decimal("96.12")
        raise ValueError(f"Unsupported pair: {base}/{quote}")
