from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery.core.db.base import Base

if TYPE_CHECKING:
    from delivery.parcel_types.db.models import ParcelTypeModel


class ParcelModel(Base):
    __tablename__ = "parcels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    parcel_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("parcel_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    weight_kg: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    delivery_cost_rub: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    parcel_type: Mapped[ParcelTypeModel] = relationship(
        "ParcelTypeModel",
        back_populates="parcels",
    )
