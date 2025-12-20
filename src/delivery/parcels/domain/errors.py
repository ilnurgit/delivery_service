from delivery.core.errors.base import AppError


class ParcelWeightMustBePositiveError(AppError):
    def __init__(self, weight_kg: float) -> None:
        super().__init__(
            code="parcel_weight_must_be_positive",
            message="Parcel weight must be positive",
            details={"weight_kg": weight_kg},
        )
