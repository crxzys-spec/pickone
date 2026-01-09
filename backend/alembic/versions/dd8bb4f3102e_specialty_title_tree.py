# Template for new Alembic revision files.

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = 'dd8bb4f3102e'
down_revision = '9c8923f9b8a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name

    def table_exists(name: str) -> bool:
        row = conn.execute(
            sa.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
            ),
            {"name": name},
        ).fetchone()
        return row is not None

    def column_exists(table: str, column: str) -> bool:
        rows = conn.execute(sa.text(f"PRAGMA table_info('{table}')")).fetchall()
        return any(row[1] == column for row in rows)

    def index_exists(table: str, index: str) -> bool:
        rows = conn.execute(sa.text(f"PRAGMA index_list('{table}')")).fetchall()
        return any(row[1] == index for row in rows)

    if dialect == "sqlite":
        if table_exists("specialties"):
            with op.batch_alter_table("specialties") as batch_op:
                if index_exists("specialties", "ix_specialties_subcategory_id"):
                    batch_op.drop_index("ix_specialties_subcategory_id")
                if index_exists("specialties", "uq_specialty_subcategory_name"):
                    batch_op.drop_constraint(
                        "uq_specialty_subcategory_name", type_="unique"
                    )
                if not column_exists("specialties", "parent_id"):
                    batch_op.add_column(sa.Column("parent_id", sa.Integer(), nullable=True))
                if column_exists("specialties", "subcategory_id"):
                    batch_op.drop_column("subcategory_id")
                if not index_exists("specialties", "ix_specialties_parent_id"):
                    batch_op.create_index(
                        "ix_specialties_parent_id", ["parent_id"], unique=False
                    )
                if not index_exists("specialties", "uq_specialty_code"):
                    batch_op.create_unique_constraint("uq_specialty_code", ["code"])

        if table_exists("titles"):
            with op.batch_alter_table("titles") as batch_op:
                if index_exists("titles", "ix_titles_name"):
                    batch_op.drop_index("ix_titles_name")
                if not column_exists("titles", "parent_id"):
                    batch_op.add_column(sa.Column("parent_id", sa.Integer(), nullable=True))
                if not index_exists("titles", "ix_titles_parent_id"):
                    batch_op.create_index(
                        "ix_titles_parent_id", ["parent_id"], unique=False
                    )
                batch_op.create_index("ix_titles_name", ["name"], unique=False)

        if table_exists("experts"):
            with op.batch_alter_table("experts") as batch_op:
                for index_name in (
                    "ix_experts_category",
                    "ix_experts_subcategory",
                    "ix_experts_category_id",
                    "ix_experts_subcategory_id",
                ):
                    if index_exists("experts", index_name):
                        batch_op.drop_index(index_name)
                for column in (
                    "email",
                    "category_id",
                    "category",
                    "subcategory_id",
                    "subcategory",
                ):
                    if column_exists("experts", column):
                        batch_op.drop_column(column)

        if table_exists("subcategories"):
            op.drop_table("subcategories")
        if table_exists("categories"):
            op.drop_table("categories")
        return

    op.drop_index("ix_specialties_subcategory_id", table_name="specialties")
    op.drop_constraint(
        "uq_specialty_subcategory_name", "specialties", type_="unique"
    )
    op.add_column("specialties", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.drop_column("specialties", "subcategory_id")
    op.create_index("ix_specialties_parent_id", "specialties", ["parent_id"], unique=False)
    op.create_unique_constraint("uq_specialty_code", "specialties", ["code"])

    op.drop_index("ix_titles_name", table_name="titles")
    op.add_column("titles", sa.Column("parent_id", sa.Integer(), nullable=True))
    op.create_index("ix_titles_parent_id", "titles", ["parent_id"], unique=False)
    op.create_index("ix_titles_name", "titles", ["name"], unique=False)

    op.drop_index("ix_experts_category", table_name="experts")
    op.drop_index("ix_experts_subcategory", table_name="experts")
    op.drop_index("ix_experts_category_id", table_name="experts")
    op.drop_index("ix_experts_subcategory_id", table_name="experts")
    op.drop_column("experts", "email")
    op.drop_column("experts", "category_id")
    op.drop_column("experts", "category")
    op.drop_column("experts", "subcategory_id")
    op.drop_column("experts", "subcategory")

    op.drop_table("subcategories")
    op.drop_table("categories")


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name

    def table_exists(name: str) -> bool:
        row = conn.execute(
            sa.text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
            ),
            {"name": name},
        ).fetchone()
        return row is not None

    if dialect == "sqlite":
        if not table_exists("categories"):
            op.create_table(
                "categories",
                sa.Column("id", sa.Integer(), nullable=False),
                sa.Column("name", sa.String(length=50), nullable=False),
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
            op.create_index("ix_categories_name", "categories", ["name"], unique=False)

        if not table_exists("subcategories"):
            op.create_table(
                "subcategories",
                sa.Column("id", sa.Integer(), nullable=False),
                sa.Column("category_id", sa.Integer(), nullable=True),
                sa.Column("name", sa.String(length=80), nullable=False),
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
            )
            op.create_index(
                "ix_subcategories_category_id",
                "subcategories",
                ["category_id"],
                unique=False,
            )

        if table_exists("specialties"):
            with op.batch_alter_table("specialties") as batch_op:
                batch_op.drop_constraint("uq_specialty_code", type_="unique")
                batch_op.drop_index("ix_specialties_parent_id")
                batch_op.drop_column("parent_id")
                batch_op.add_column(sa.Column("subcategory_id", sa.Integer(), nullable=True))
                batch_op.create_index(
                    "ix_specialties_subcategory_id", ["subcategory_id"], unique=False
                )
                batch_op.create_unique_constraint(
                    "uq_specialty_subcategory_name", ["subcategory_id", "name"]
                )

        if table_exists("titles"):
            with op.batch_alter_table("titles") as batch_op:
                batch_op.drop_index("ix_titles_parent_id")
                batch_op.drop_index("ix_titles_name")
                batch_op.drop_column("parent_id")
                batch_op.create_index("ix_titles_name", ["name"], unique=True)

        if table_exists("experts"):
            with op.batch_alter_table("experts") as batch_op:
                batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
                batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
                batch_op.add_column(sa.Column("category", sa.String(length=50), nullable=True))
                batch_op.add_column(
                    sa.Column("subcategory_id", sa.Integer(), nullable=True)
                )
                batch_op.add_column(
                    sa.Column("subcategory", sa.String(length=80), nullable=True)
                )
                batch_op.create_index(
                    "ix_experts_category", ["category"], unique=False
                )
                batch_op.create_index(
                    "ix_experts_subcategory", ["subcategory"], unique=False
                )
                batch_op.create_index(
                    "ix_experts_category_id", ["category_id"], unique=False
                )
                batch_op.create_index(
                    "ix_experts_subcategory_id", ["subcategory_id"], unique=False
                )
        return

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
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
    op.create_index("ix_categories_name", "categories", ["name"], unique=False)

    op.create_table(
        "subcategories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=80), nullable=False),
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
    )
    op.create_index(
        "ix_subcategories_category_id", "subcategories", ["category_id"], unique=False
    )

    op.drop_constraint("uq_specialty_code", "specialties", type_="unique")
    op.drop_index("ix_specialties_parent_id", table_name="specialties")
    op.drop_column("specialties", "parent_id")
    op.add_column("specialties", sa.Column("subcategory_id", sa.Integer(), nullable=True))
    op.create_index(
        "ix_specialties_subcategory_id", "specialties", ["subcategory_id"], unique=False
    )
    op.create_unique_constraint(
        "uq_specialty_subcategory_name", "specialties", ["subcategory_id", "name"]
    )

    op.drop_index("ix_titles_parent_id", table_name="titles")
    op.drop_index("ix_titles_name", table_name="titles")
    op.drop_column("titles", "parent_id")
    op.create_index("ix_titles_name", "titles", ["name"], unique=True)

    op.add_column("experts", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("experts", sa.Column("category_id", sa.Integer(), nullable=True))
    op.add_column("experts", sa.Column("category", sa.String(length=50), nullable=True))
    op.add_column("experts", sa.Column("subcategory_id", sa.Integer(), nullable=True))
    op.add_column("experts", sa.Column("subcategory", sa.String(length=80), nullable=True))
    op.create_index("ix_experts_category", "experts", ["category"], unique=False)
    op.create_index("ix_experts_subcategory", "experts", ["subcategory"], unique=False)
    op.create_index("ix_experts_category_id", "experts", ["category_id"], unique=False)
    op.create_index(
        "ix_experts_subcategory_id", "experts", ["subcategory_id"], unique=False
    )
