from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx

from delivery.fx.provider import FxRateProvider


@dataclass(slots=True)
class CbrXmlDailyProvider(FxRateProvider):
    url: str = "https://www.cbr-xml-daily.ru/daily_json.js"
    timeout_s: float = 5.0

    async def get_rate(self, base: str, quote: str) -> Decimal:
        if (base, quote) != ("USD", "RUB"):
            raise ValueError(f"Unsupported pair: {base}/{quote}")

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            r = await client.get(self.url)
            r.raise_for_status()
            data: dict[str, Any] = r.json()

        usd = data["Valute"]["USD"]
        value = Decimal(str(usd["Value"]))
        nominal = Decimal(str(usd["Nominal"]))
        return value / nominal
