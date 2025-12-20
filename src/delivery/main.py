from fastapi import FastAPI

from delivery.api.router import router as api_router
from delivery.core.api.health import router as health_router
from delivery.core.errors.base import AppError
from delivery.core.errors.handlers import app_error_handler


def create_app() -> FastAPI:
    app = FastAPI(
        title="Delivery Service",
        version="0.1.0",
    )
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    app.add_exception_handler(AppError, app_error_handler)

    return app


app = create_app()
