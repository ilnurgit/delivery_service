from __future__ import annotations

from pydantic import BaseModel, Field


class ParcelCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    parcel_type_code: str = Field(..., min_length=1, max_length=32)
    weight_kg: float = Field(..., gt=0)
    content_usd: str = Field(..., pattern=r"^\d+(\.\d{1,2})?$")


class ParcelOut(BaseModel):
    id: str
    title: str
    parcel_type_id: str
    parcel_type_code: str | None = None
    parcel_type_name: str | None = None
    weight_kg: float
    content_usd: str
    delivery_cost_rub: str | None = None
