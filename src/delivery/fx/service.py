from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from delivery.fx.cache import FxRateCache
from delivery.fx.provider import FxRateProvider


@dataclass(slots=True)
class FxService:
    cache: FxRateCache
    provider: FxRateProvider

    async def get_rate(self, base: str, quote: str) -> Decimal:
        cached = await self.cache.get_rate(base=base, quote=quote)
        if cached is not None:
            return cached

        rate = await self.provider.get_rate(base=base, quote=quote)
        await self.cache.set_rate(base=base, quote=quote, rate=rate)
        return rate
