from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery.core.db.base import Base

if TYPE_CHECKING:
    from delivery.parcels.db.models import ParcelModel


class ParcelTypeModel(Base):
    __tablename__ = "parcel_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    base_price_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price_per_kg_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    parcels: Mapped[list[ParcelModel]] = relationship(
        "ParcelModel",
        back_populates="parcel_type",
    )
