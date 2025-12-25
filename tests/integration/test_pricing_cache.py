from decimal import Decimal

import pytest

from delivery.pricing.services.calculator import CostCalculator

pytestmark = pytest.mark.integration


class CountingFx:
    def __init__(self):
        self.calls = 0

    async def get_rate(self, base: str, quote: str) -> Decimal:
        self.calls += 1
        return Decimal("96.12")


class FakeTypeRepo:
    async def get_by_code(self, code: str):
        return type(
            "PT",
            (),
            {
                "id": "x",
                "code": code,
                "name": "Documents",
                "base_price_usd": "5.00",
                "price_per_kg_usd": "2.50",
            },
        )()


async def test_calculator_calls_fx_once_for_rub():
    fx = CountingFx()
    calc = CostCalculator(type_repo=FakeTypeRepo(), fx=fx)

    money = await calc.calculate("DOC", 2, "RUB")
    assert money.currency == "RUB"
    assert fx.calls == 1
