from fastapi import HTTPException as FastAPIHTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from delivery.core.errors.base import AppError
from delivery.core.errors.envelope import build_error

_APP_ERROR_STATUS: dict[str, int] = {
    # parcel types
    "parcel_type_not_found": status.HTTP_404_NOT_FOUND,
    "parcel_type_already_exists": status.HTTP_409_CONFLICT,
}


def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_code = _APP_ERROR_STATUS.get(exc.code, status.HTTP_400_BAD_REQUEST)
    return JSONResponse(
        status_code=status_code,
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
