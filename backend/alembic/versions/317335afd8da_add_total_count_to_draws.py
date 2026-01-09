# Template for new Alembic revision files.

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '317335afd8da'
down_revision = 'dd8bb4f3102e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_total = False
    not_null = False

    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(draw_applications)")).fetchall()
        for row in rows:
            if row[1] == "total_count":
                has_total = True
                not_null = bool(row[3])
                break
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("draw_applications")
        has_total = any(col["name"] == "total_count" for col in columns)

    if not has_total:
        op.add_column(
            "draw_applications",
            sa.Column("total_count", sa.Integer(), nullable=True),
        )

    if not not_null:
        op.execute(
            "UPDATE draw_applications SET total_count = expert_count WHERE total_count IS NULL"
        )
        if dialect != "sqlite":
            op.alter_column(
                "draw_applications",
                "total_count",
                existing_type=sa.Integer(),
                nullable=False,
            )


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    has_total = False
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA table_info(draw_applications)")).fetchall()
        has_total = any(row[1] == "total_count" for row in rows)
    else:
        inspector = sa.inspect(conn)
        columns = inspector.get_columns("draw_applications")
        has_total = any(col["name"] == "total_count" for col in columns)

    if has_total:
        op.drop_column("draw_applications", "total_count")
