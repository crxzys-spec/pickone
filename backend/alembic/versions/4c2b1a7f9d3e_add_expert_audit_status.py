# Template for new Alembic revision files.

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4c2b1a7f9d3e"
down_revision = "317335afd8da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_column = False
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(experts)")).fetchall()
        has_column = any(row[1] == "audit_status" for row in rows)
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("experts")
        has_column = any(col["name"] == "audit_status" for col in columns)

    if not has_column:
        op.add_column(
            "experts",
            sa.Column(
                "audit_status",
                sa.String(length=20),
                nullable=False,
                server_default="pending",
            ),
        )
        op.execute("UPDATE experts SET audit_status = 'approved'")


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_column = False
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(experts)")).fetchall()
        has_column = any(row[1] == "audit_status" for row in rows)
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("experts")
        has_column = any(col["name"] == "audit_status" for col in columns)

    if has_column:
        op.drop_column("experts", "audit_status")
