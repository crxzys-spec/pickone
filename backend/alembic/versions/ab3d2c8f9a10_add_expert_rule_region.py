"""add expert region and rule region

Revision ID: ab3d2c8f9a10
Revises: f12c9d7b3b64
Create Date: 2025-01-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ab3d2c8f9a10"
down_revision = "f12c9d7b3b64"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("experts") as batch_op:
        batch_op.add_column(sa.Column("region", sa.String(length=80), nullable=True))
        batch_op.create_index("ix_experts_region", ["region"])

    with op.batch_alter_table("rules") as batch_op:
        batch_op.add_column(
            sa.Column("region_required", sa.String(length=80), nullable=True)
        )
        batch_op.create_index("ix_rules_region_required", ["region_required"])


def downgrade() -> None:
    with op.batch_alter_table("rules") as batch_op:
        batch_op.drop_index("ix_rules_region_required")
        batch_op.drop_column("region_required")

    with op.batch_alter_table("experts") as batch_op:
        batch_op.drop_index("ix_experts_region")
        batch_op.drop_column("region")
