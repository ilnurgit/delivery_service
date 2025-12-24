from fastapi import APIRouter
from fastapi.responses import JSONResponse
from loguru import logger

router = APIRouter()


@router.get("/health", tags=["system"])
async def health() -> JSONResponse:
    logger.info("Hello from handler")
    return JSONResponse({"status": "ok"})
