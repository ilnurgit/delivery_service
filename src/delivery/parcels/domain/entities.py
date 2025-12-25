from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Parcel:
    id: str
    session_id: str
    parcel_type_id: str
    parcel_type_code: str
    parcel_type_name: str | None
    title: str
    weight_kg: float
    content_usd: str
    delivery_cost_rub: str | None
