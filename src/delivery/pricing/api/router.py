from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.di.db import get_db_session
from delivery.parcel_types.repositories.sqlalchemy import SqlAlchemyParcelTypeRepository
from delivery.pricing.api.schemas import CostCalcIn, CostCalcOut
from delivery.pricing.services.calculator import CostCalculator

router = APIRouter(prefix="/pricing", tags=["pricing"])


def get_calc(session: AsyncSession = Depends(get_db_session)) -> CostCalculator:
    return CostCalculator(SqlAlchemyParcelTypeRepository(session))


@router.post("/calculate", response_model=CostCalcOut)
async def calculate_cost(
    payload: CostCalcIn, calc: CostCalculator = Depends(get_calc)
) -> CostCalcOut:
    money = await calc.calculate_usd(payload.parcel_type_code, payload.weight_kg)
    return CostCalcOut(amount=str(money.amount), currency=money.currency)
