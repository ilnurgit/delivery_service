from __future__ import annotations

from pydantic import BaseModel, Field


class CostCalcIn(BaseModel):
    parcel_type_code: str = Field(..., min_length=1, max_length=32)
    weight_kg: float = Field(..., gt=0)
    currency: str = Field(default="USD", pattern="^(USD|RUB)$")


class CostCalcOut(BaseModel):
    amount: str
    currency: str
