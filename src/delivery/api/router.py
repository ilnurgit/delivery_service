from fastapi import APIRouter

from delivery.fx.api.router import router as fx_router
from delivery.fx.api.tasks_router import router as task_router
from delivery.parcel_types.api.router import router as parcel_types_router
from delivery.parcels.api.router import router as parcels_router
from delivery.pricing.api.router import router as pricing_router

router = APIRouter()
router.include_router(parcels_router)
router.include_router(parcel_types_router)
router.include_router(pricing_router)
router.include_router(fx_router)
router.include_router(task_router)
