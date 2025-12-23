from fastapi import HTTPException as FastAPIHTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from delivery.core.errors.base import AppError
from delivery.core.errors.envelope import build_error


def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=build_error(
            request=request,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


def http_exception_handler(
    request: Request, exc: FastAPIHTTPException | StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error(
            request=request,
            code="http_error",
            message="HTTP error",
            details={"detail": exc.detail},
        ),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=build_error(
            request=request,
            code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        ),
    )
