from __future__ import annotations

from uuid import uuid4

from fastapi import Cookie, Request

SESSION_COOKIE = "delivery_session_id"


def get_session_id(
    request: Request,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> str:
    if session_id:
        return session_id

    sid = getattr(request.state, "session_id", None)
    if sid:
        return sid

    sid = str(uuid4())
    request.state.session_id = sid
    return sid
