from __future__ import annotations

from delivery.parcel_types.api.schemas import ParcelTypeOut
from delivery.parcel_types.domain.entities import ParcelType


def to_out(pt: ParcelType) -> ParcelTypeOut:
    return ParcelTypeOut(id=pt.id, code=pt.code, name=pt.name)


def to_out_list(items: list[ParcelType]) -> list[ParcelTypeOut]:
    return [to_out(i) for i in items]
