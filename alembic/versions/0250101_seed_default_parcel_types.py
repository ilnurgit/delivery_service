"""seed default parcel types

Revision ID: 20250101_seed_parcel_types
Revises: aa5125124665
Create Date: 2025-01-01 12:00:00
"""

from __future__ import annotations

from alembic import op

# --- Alembic identifiers ---
revision: str = "20250101_seed_parcel_types"
down_revision: str | None = "aa5125124665"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # на всякий случай — если uuid генерируется через pgcrypto
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.execute(
        """
        INSERT INTO parcel_types (id, code, name, base_price_usd, price_per_kg_usd)
        VALUES
          (gen_random_uuid(), 'DOC', 'Documents', 5.00, 0.00),
          (gen_random_uuid(), 'BOX', 'Box', 10.00, 2.50)
        ON CONFLICT (code) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM parcel_types
        WHERE code IN ('DOC', 'BOX');
        """
    )
