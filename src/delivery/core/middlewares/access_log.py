from __future__ import annotations

import time

from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from delivery.core.logging_context import trace_id_var


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()

        trace_id = getattr(request.state, "trace_id", None)
        token = trace_id_var.set(trace_id)

        try:
            response = await call_next(request)
            return response
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = getattr(locals().get("response"), "status_code", 500)

            logger.info(
                "{method} {path} -> {status} ({elapsed_ms:.1f}ms)",
                method=request.method,
                path=request.url.path,
                status=status,
                elapsed_ms=elapsed_ms,
            )

            trace_id_var.reset(token)
