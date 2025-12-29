"""add draw project name

Revision ID: e2f9a7c3b1d4
Revises: d1c5a8f0b6e2
Create Date: 2025-01-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e2f9a7c3b1d4"
down_revision = "d1c5a8f0b6e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.add_column(sa.Column("project_name", sa.String(length=255), nullable=True))
        batch_op.create_index(
            "ix_draw_applications_project_name", ["project_name"]
        )


def downgrade() -> None:
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.drop_index("ix_draw_applications_project_name")
        batch_op.drop_column("project_name")
