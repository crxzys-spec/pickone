# Template for new Alembic revision files.
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a3c7f92d0b1e"
down_revision = "ce9efe7a70d0"
branch_labels = None
depends_on = None


def _sqlite_index_map(conn, table_name: str) -> dict[str, tuple]:
    rows = conn.execute(sa.text(f"PRAGMA index_list('{table_name}')")).fetchall()
    return {row[1]: row for row in rows}


def _sqlite_table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        sa.text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
        ),
        {"name": table_name},
    ).fetchone()
    return row is not None


def upgrade() -> None:
    conn = op.get_bind()
    if conn.dialect.name == "sqlite":
        indexes = _sqlite_index_map(conn, "categories")
        index_name = "ix_categories_name"
        index_row = indexes.get(index_name)
        if index_row is None:
            op.create_index(index_name, "categories", ["name"], unique=False)
        else:
            is_unique = bool(index_row[2])
            if is_unique:
                op.drop_index(index_name, table_name="categories")
                op.create_index(index_name, "categories", ["name"], unique=False)

        if _sqlite_table_exists(conn, "specialties"):
            indexes = _sqlite_index_map(conn, "specialties")
            if "uq_specialty_subcategory_name" in indexes:
                with op.batch_alter_table("specialties") as batch_op:
                    batch_op.drop_constraint(
                        "uq_specialty_subcategory_name", type_="unique"
                    )
        return

    op.drop_index("ix_categories_name", table_name="categories")
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)
    with op.batch_alter_table("specialties") as batch_op:
        batch_op.drop_constraint("uq_specialty_subcategory_name", type_="unique")


def downgrade() -> None:
    op.drop_index("ix_categories_name", table_name="categories")
    op.create_index("ix_categories_name", "categories", ["name"], unique=True)
    with op.batch_alter_table("specialties") as batch_op:
        batch_op.create_unique_constraint(
            "uq_specialty_subcategory_name", ["subcategory_id", "name"]
        )
