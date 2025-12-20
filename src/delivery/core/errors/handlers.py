from fastapi import Request
from fastapi.responses import JSONResponse

from delivery.core.errors.base import AppError


def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
