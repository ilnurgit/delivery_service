from delivery.parcels.api.schemas import ParcelOut
from delivery.parcels.domain.entities import Parcel


def to_parcel_out(parcel: Parcel) -> ParcelOut:
    return ParcelOut(id=parcel.id, parcel_type_id=parcel.parcel_type_id, weight_kg=parcel.weight_kg)


def to_parcel_out_list(items: list[Parcel]) -> list[ParcelOut]:
    return [to_parcel_out(i) for i in items]
