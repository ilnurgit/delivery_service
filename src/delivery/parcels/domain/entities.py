from dataclasses import dataclass


@dataclass(slots=True)
class Parcel:
    id: str
    parcel_type_id: str
    weight_kg: float
