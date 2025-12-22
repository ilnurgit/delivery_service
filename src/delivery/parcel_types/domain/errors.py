from __future__ import annotations

from delivery.core.errors.base import AppError


class ParcelTypeNotFoundError(AppError):
    def __init__(self, code: str) -> None:
        super().__init__(
            code="parcel_type_not_found",
            message="Parcel type not found",
            details={"code": code},
        )
