from __future__ import annotations

from delivery.parcels.api.schemas import ParcelOut
from delivery.parcels.domain.entities import Parcel


def to_parcel_out(parcel: Parcel) -> ParcelOut:
    display = parcel.delivery_cost_rub if parcel.delivery_cost_rub is not None else "Не рассчитано"
    return ParcelOut(
        id=parcel.id,
        title=parcel.title,
        parcel_type_id=parcel.parcel_type_id,
        parcel_type_code=parcel.parcel_type_code,
        parcel_type_name=parcel.parcel_type_name,
        weight_kg=parcel.weight_kg,
        content_usd=parcel.content_usd,
        delivery_cost_rub=parcel.delivery_cost_rub,
        delivery_cost_rub_display=display,
    )


def to_parcel_out_list(items: list[Parcel]) -> list[ParcelOut]:
    return [to_parcel_out(p) for p in items]
