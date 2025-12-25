from dataclasses import dataclass


@dataclass(slots=True)
class ParcelType:
    id: str
    code: str
    name: str
    base_price_usd: str
    price_per_kg_usd: str
