from pydantic import BaseModel, Field


class ParcelCreate(BaseModel):
    parcel_type_id: str = Field(..., description="Parcel type identifier")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")


class ParcelOut(BaseModel):
    id: str
    parcel_type_id: str
    weight_kg: float
