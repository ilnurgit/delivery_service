from dataclasses import dataclass


@dataclass(slots=True)
class ParcelType:
    id: str
    code: str
    name: str
