"""Product data access layer."""

import uuid

from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.orm import Session

from app.core.pagination import ProductCursor
from app.models.product import Product
from app.schemas.product import ProductCreate


def _escape_ilike(value: str) -> str:
    """Escape ILIKE wildcard characters in user-provided search text."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class ProductRepository:
    """Encapsulates all SQL operations for the products table."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, data: ProductCreate) -> Product:
        """Insert a single product and return the persisted row."""
        product = Product(
            id=uuid.uuid4(),
            name=data.name,
            category=data.category,
            price=data.price,
        )
        self._db.add(product)
        self._db.flush()
        self._db.refresh(product)
        return product

    def bulk_create(self, items: list[ProductCreate]) -> int:
        """
        Insert many products in one round-trip using a multi-row INSERT.

        Returns the number of rows inserted.
        """
        if not items:
            return 0

        rows = [
            {
                "id": uuid.uuid4(),
                "name": item.name,
                "category": item.category,
                "price": item.price,
            }
            for item in items
        ]
        self._db.execute(insert(Product), rows)
        self._db.flush()
        return len(rows)

    def count(self) -> int:
        """Return total number of products in the catalog."""
        total = self._db.scalar(select(func.count()).select_from(Product))
        return int(total or 0)

    def get_products_page(
        self,
        *,
        limit: int,
        cursor: ProductCursor | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Product], bool]:
        """
        Fetch one keyset page ordered by updated_at DESC, id DESC.

        Uses composite tuple comparison — never OFFSET.
        Fetches limit + 1 rows to detect whether a next page exists.
        """
        stmt = select(Product)

        if category is not None:
            stmt = stmt.where(Product.category == category)

        if search is not None:
            escaped = _escape_ilike(search)
            # ILIKE '%term%' — accelerated by ix_products_name_trgm_gin (pg_trgm GIN index).
            stmt = stmt.where(Product.name.ilike(f"%{escaped}%", escape="\\"))

        if cursor is not None:
            stmt = stmt.where(
                or_(
                    Product.updated_at < cursor.updated_at,
                    and_(
                        Product.updated_at == cursor.updated_at,
                        Product.id < cursor.id,
                    ),
                )
            )

        stmt = (
            stmt.order_by(Product.updated_at.desc(), Product.id.desc())
            .limit(limit + 1)
        )

        rows = list(self._db.scalars(stmt).all())
        has_more = len(rows) > limit
        return rows[:limit], has_more
