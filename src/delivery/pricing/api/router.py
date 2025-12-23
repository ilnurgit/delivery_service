from __future__ import annotations

from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.core.di.db import get_db_session
from delivery.core.di.redis import get_redis
from delivery.fx.cache import FxRateCache
from delivery.fx.provider import FxRateProvider
from delivery.fx.service import FxService
from delivery.parcel_types.repositories.sqlalchemy import SqlAlchemyParcelTypeRepository
from delivery.pricing.api.schemas import CostCalcIn, CostCalcOut
from delivery.pricing.services.calculator import CostCalculator

router = APIRouter(prefix="/pricing", tags=["pricing"])


def get_calc(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),
) -> CostCalculator:
    type_repo = SqlAlchemyParcelTypeRepository(session)
    cache = FxRateCache(redis=redis, ttl_seconds=300)
    fx = FxService(cache=cache, provider=FxRateProvider())
    return CostCalculator(type_repo=type_repo, fx=fx)


@router.post("/calculate", response_model=CostCalcOut)
async def calculate_cost(
    payload: CostCalcIn, calc: CostCalculator = Depends(get_calc)
) -> CostCalcOut:
    money = await calc.calculate(
        parcel_type_code=payload.parcel_type_code,
        weight_kg=payload.weight_kg,
        currency=payload.currency,
    )
    return CostCalcOut(amount=str(money.amount), currency=money.currency)
