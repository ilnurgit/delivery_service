from fastapi import FastAPI

from delivery.core.api.health import router as health_router
from delivery.parcels.api.router import router as parcels_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Delivery Service",
        version="0.1.0",
    )
    app.include_router(health_router)
    app.include_router(parcels_router)
    return app


app = create_app()
