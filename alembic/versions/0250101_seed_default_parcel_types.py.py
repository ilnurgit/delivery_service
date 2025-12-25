"""seed default parcel types

Revision ID: 20250101_seed_parcel_types
Revises: aa5125124665
Create Date: 2025-01-01 12:00:00
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

# --- Alembic identifiers ---
revision: str = "20250101_seed_parcel_types"
down_revision: str | None = "aa5125124665"
branch_labels = None
depends_on = None


def upgrade() -> None:
    parcel_types = sa.table(
        "parcel_types",
        sa.column("id", sa.Uuid()),
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("base_price_usd", sa.Numeric(10, 2)),
        sa.column("price_per_kg_usd", sa.Numeric(10, 2)),
    )

    op.bulk_insert(
        parcel_types,
        [
            {
                "id": uuid.uuid4(),
                "code": "DOC",
                "name": "Documents",
                "base_price_usd": Decimal("5.00"),
                "price_per_kg_usd": Decimal("0.00"),
            },
            {
                "id": uuid.uuid4(),
                "code": "BOX",
                "name": "Box",
                "base_price_usd": Decimal("10.00"),
                "price_per_kg_usd": Decimal("2.50"),
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM parcel_types
        WHERE code IN ('DOC', 'BOX')
        """
    )
