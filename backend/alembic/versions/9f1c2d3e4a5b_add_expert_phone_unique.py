# Template for new Alembic revision files.

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f1c2d3e4a5b"
down_revision = "4c2b1a7f9d3e"
branch_labels = None
depends_on = None


def _has_index(conn, index_name: str) -> bool:
    dialect = conn.dialect.name
    if dialect == "sqlite":
        rows = conn.execute(sa.text("PRAGMA index_list(experts)")).fetchall()
        return any(row[1] == index_name for row in rows)
    inspector = sa.inspect(conn)
    indexes = inspector.get_indexes("experts")
    return any(index.get("name") == index_name for index in indexes)


def upgrade() -> None:
    conn = op.get_bind()
    index_name = "ix_experts_phone"
    if not _has_index(conn, index_name):
        op.create_index(index_name, "experts", ["phone"], unique=True)


def downgrade() -> None:
    conn = op.get_bind()
    index_name = "ix_experts_phone"
    if _has_index(conn, index_name):
        op.drop_index(index_name, table_name="experts")
