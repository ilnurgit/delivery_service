from __future__ import annotations

from fastapi import APIRouter

from delivery.pricing.api.schemas import CostCalcIn, CostCalcOut
from delivery.pricing.services.calculator import CostCalculator

router = APIRouter(prefix="/pricing", tags=["pricing"])

_calc = CostCalculator()


@router.post("/calculate", response_model=CostCalcOut)
async def calculate_cost(payload: CostCalcIn) -> CostCalcOut:
    money = _calc.calculate_usd(payload.parcel_type_code, payload.weight_kg)
    return CostCalcOut(amount=str(money.amount), currency=money.currency)
