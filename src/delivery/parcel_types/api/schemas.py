from __future__ import annotations

from pydantic import BaseModel, Field


class ParcelTypeCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32)
    name: str = Field(..., min_length=1, max_length=128)


class ParcelTypeOut(BaseModel):
    id: str
    code: str
    name: str
