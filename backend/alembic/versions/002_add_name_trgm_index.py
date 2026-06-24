"""Enable pg_trgm and add GIN trigram index on products.name.

Revision ID: 002_add_name_trgm_index
Revises: 001_create_products
Create Date: 2026-06-24

"""

from typing import Sequence, Union

from alembic import op

revision: str = "002_add_name_trgm_index"
down_revision: Union[str, None] = "001_create_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.create_index(
        "ix_products_name_trgm_gin",
        "products",
        ["name"],
        unique=False,
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_products_name_trgm_gin",
        table_name="products",
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    # pg_trgm is left installed; other objects in the database may depend on it.
