from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from delivery.core.money import Money


def convert(money: Money, rate: Decimal, target_currency: str) -> Money:
    amount = (money.amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Money(amount=amount, currency=target_currency)
