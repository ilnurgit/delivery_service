from fastapi import APIRouter

from delivery.parcels.api.router import router as parcels_router

router = APIRouter()
router.include_router(parcels_router)
