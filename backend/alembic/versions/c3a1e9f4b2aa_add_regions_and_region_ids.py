"""add regions and region ids

Revision ID: c3a1e9f4b2aa
Revises: ab3d2c8f9a10
Create Date: 2025-01-06 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3a1e9f4b2aa"
down_revision = "ab3d2c8f9a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_regions_name"), "regions", ["name"], unique=True)

    op.add_column("experts", sa.Column("region_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_experts_region_id"), "experts", ["region_id"], unique=False
    )

    op.add_column("rules", sa.Column("region_required_id", sa.Integer(), nullable=True))
    op.create_index(
        op.f("ix_rules_region_required_id"),
        "rules",
        ["region_required_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_rules_region_required_id"), table_name="rules")
    op.drop_column("rules", "region_required_id")

    op.drop_index(op.f("ix_experts_region_id"), table_name="experts")
    op.drop_column("experts", "region_id")

    op.drop_index(op.f("ix_regions_name"), table_name="regions")
    op.drop_table("regions")
