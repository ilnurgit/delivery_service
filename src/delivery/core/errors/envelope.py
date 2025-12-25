from __future__ import annotations

from fastapi import Request


def build_error(
    *,
    request: Request,
    code: str,
    message: str,
    details: dict | list | str | None = None,
) -> dict:
    trace_id = getattr(request.state, "trace_id", None)
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "trace_id": trace_id,
        }
    }
