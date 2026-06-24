"""Product business logic."""

from app.core.categories import is_valid_category
from app.core.pagination import (
    InvalidCursorError,
    decode_product_cursor,
    encode_product_cursor,
)
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse


class InvalidCategoryError(ValueError):
    """Raised when a product category is not in configuration."""


class ProductService:
    """Orchestrates product operations and enforces domain rules."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def create_product(self, data: ProductCreate) -> ProductResponse:
        """Validate and persist a single product."""
        self._ensure_valid_category(data.category)
        product = self._repository.create(data)
        return ProductResponse.model_validate(product)

    def bulk_create_products(self, items: list[ProductCreate]) -> int:
        """Validate and persist many products via batch insert."""
        for item in items:
            self._ensure_valid_category(item.category)
        return self._repository.bulk_create(items)

    def total_products(self) -> int:
        """Return the catalog size."""
        return self._repository.count()

    def list_products(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> ProductListResponse:
        """
        Return a keyset-paginated slice of the catalog.

        Decodes the opaque cursor, applies optional filters, and builds
        the pagination envelope with next_cursor and has_more.
        """
        if category is not None:
            self._ensure_valid_category(category)

        parsed_cursor = decode_product_cursor(cursor) if cursor is not None else None

        normalized_search = search.strip() if search is not None else None
        if normalized_search == "":
            normalized_search = None

        items, has_more = self._repository.get_products_page(
            limit=limit,
            cursor=parsed_cursor,
            category=category,
            search=normalized_search,
        )

        responses = [ProductResponse.model_validate(product) for product in items]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_product_cursor(last.updated_at, last.id)

        return ProductListResponse(
            items=responses,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    @staticmethod
    def _ensure_valid_category(category: str) -> None:
        if not is_valid_category(category):
            raise InvalidCategoryError(
                f"Category '{category}' is not configured. "
                "Update backend/config/categories.json to add it."
            )


__all__ = ["InvalidCategoryError", "InvalidCursorError", "ProductService"]
