# Template for new Alembic revision files.

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f7c2c11e0ab"
down_revision = "317335afd8da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_column = False
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(draw_results)")).fetchall()
        has_column = any(row[1] == "contact_status" for row in rows)
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("draw_results")
        has_column = any(col["name"] == "contact_status" for col in columns)

    if not has_column:
        op.add_column(
            "draw_results",
            sa.Column("contact_status", sa.String(length=20), nullable=True),
        )


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_column = False
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(draw_results)")).fetchall()
        has_column = any(row[1] == "contact_status" for row in rows)
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("draw_results")
        has_column = any(col["name"] == "contact_status" for col in columns)

    if has_column:
        op.drop_column("draw_results", "contact_status")
