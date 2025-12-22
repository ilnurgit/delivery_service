from pydantic import BaseModel, Field


class ParcelCreate(BaseModel):
    parcel_type_code: str = Field(..., min_length=1, max_length=32, description="Parcel type code")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")


class ParcelOut(BaseModel):
    id: str
    parcel_type_id: str
    weight_kg: float
