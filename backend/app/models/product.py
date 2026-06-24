"""Product ORM model."""

import uuid
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Index, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.base import TimestampMixin


class Product(Base, TimestampMixin):
    """
    Catalog product entity.

    UUID primary keys avoid sequential hotspot contention under bulk inserts
    and simplify distributed ID generation at scale.
    """

    __tablename__ = "products"
    __table_args__ = (
        Index(
            "ix_products_updated_at_id_desc",
            "updated_at",
            "id",
            postgresql_ops={"updated_at": "DESC", "id": "DESC"},
        ),
        Index(
            "ix_products_category_updated_at_id_desc",
            "category",
            "updated_at",
            "id",
            postgresql_ops={"updated_at": "DESC", "id": "DESC"},
        ),
        Index(
            "ix_products_name_trgm_gin",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
