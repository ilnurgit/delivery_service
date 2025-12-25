from __future__ import annotations

import sys

from loguru import logger

from delivery.core.logging_context import trace_id_var


def _patch_record(record: dict) -> None:
    record["extra"]["trace_id"] = trace_id_var.get()


def setup_logging() -> None:
    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "trace_id={extra[trace_id]} | "
            "{message}"
        ),
    )

    logger.configure(patcher=_patch_record)
