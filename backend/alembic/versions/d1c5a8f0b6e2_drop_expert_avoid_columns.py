# Template for new Alembic revision files.
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d1c5a8f0b6e2"
down_revision = "b7f2a1c4d6e9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("experts") as batch_op:
        batch_op.drop_column("avoid_persons")
        batch_op.drop_column("avoid_units")


def downgrade() -> None:
    with op.batch_alter_table("experts") as batch_op:
        batch_op.add_column(sa.Column("avoid_units", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column("avoid_persons", sa.String(length=255), nullable=True)
        )
