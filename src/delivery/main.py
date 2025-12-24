from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from delivery.api.router import router as api_router
from delivery.core.api.health import router as health_router
from delivery.core.errors.base import AppError
from delivery.core.errors.handlers import (
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
)
from delivery.core.logging import setup_logging
from delivery.core.middlewares.access_log import AccessLogMiddleware
from delivery.core.middlewares.trace_id import TraceIdMiddleware

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Delivery Service",
        version="0.1.0",
    )
    app.include_router(health_router)
    app.include_router(api_router, prefix="/api/v1")

    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(TraceIdMiddleware)

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app


app = create_app()
