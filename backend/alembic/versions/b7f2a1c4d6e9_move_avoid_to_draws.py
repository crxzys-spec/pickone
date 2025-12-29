# Template for new Alembic revision files.
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b7f2a1c4d6e9"
down_revision = "a3c7f92d0b1e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.add_column(sa.Column("avoid_units", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column("avoid_persons", sa.String(length=255), nullable=True)
        )
    with op.batch_alter_table("rules") as batch_op:
        batch_op.drop_column("avoid_enabled")


def downgrade() -> None:
    with op.batch_alter_table("rules") as batch_op:
        batch_op.add_column(
            sa.Column(
                "avoid_enabled",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )
    with op.batch_alter_table("draw_applications") as batch_op:
        batch_op.drop_column("avoid_persons")
        batch_op.drop_column("avoid_units")
