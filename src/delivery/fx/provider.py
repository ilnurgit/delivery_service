from __future__ import annotations

from decimal import Decimal
from typing import Protocol


class FxRateProvider(Protocol):
    async def get_rate(self, base: str, quote: str) -> Decimal: ...
