from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

SESSION_COOKIE_NAME = "delivery_session_id"
SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 дней


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        session_id = request.cookies.get(SESSION_COOKIE_NAME)

        if session_id is None:
            session_id = str(uuid.uuid4())
            request.state.session_id = session_id
            response = await call_next(request)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session_id,
                max_age=SESSION_MAX_AGE,
                httponly=True,
                samesite="lax",
            )
            return response

        request.state.session_id = session_id
        return await call_next(request)
