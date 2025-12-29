"""add draw project code

Revision ID: f12c9d7b3b64
Revises: e2f9a7c3b1d4
Create Date: 2025-01-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f12c9d7b3b64"
down_revision = "e2f9a7c3b1d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.add_column(sa.Column("project_code", sa.String(length=120), nullable=True))
        batch_op.create_index(
            "ix_draw_applications_project_code", ["project_code"]
        )


def downgrade() -> None:
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.drop_index("ix_draw_applications_project_code")
        batch_op.drop_column("project_code")
