from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from redis.asyncio import Redis


@dataclass(slots=True)
class FxRateCache:
    redis: Redis
    ttl_seconds: int = 300

    def _key(self, base: str, quote: str) -> str:
        return f"fx:{base}:{quote}"

    async def get_rate(self, base: str, quote: str) -> Decimal | None:
        value = await self.redis.get(self._key(base, quote))
        if value is None:
            return None
        return Decimal(value)

    async def set_rate(self, base: str, quote: str, rate: Decimal) -> None:
        await self.redis.set(self._key(base, quote), str(rate), ex=self.ttl_seconds)
