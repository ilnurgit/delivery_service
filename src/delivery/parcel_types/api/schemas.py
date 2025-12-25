from __future__ import annotations

from pydantic import BaseModel, Field


class ParcelTypeCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)
    base_price_usd: str = Field(..., pattern=r"^\d+(\.\d{1,2})?$")
    price_per_kg_usd: str = Field(..., pattern=r"^\d+(\.\d{1,2})?$")


class ParcelTypeOut(BaseModel):
    id: str
    code: str
    name: str
    base_price_usd: str
    price_per_kg_usd: str
