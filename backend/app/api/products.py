"""Product catalog API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductListResponse
from app.services.product_service import (
    InvalidCategoryError,
    InvalidCursorError,
    ProductService,
)

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Provide a request-scoped ProductService."""
    return ProductService(ProductRepository(db))


@router.get("", response_model=ProductListResponse, summary="List products")
def list_products(
    limit: int = Query(default=20, ge=1, le=100, description="Page size."),
    cursor: str | None = Query(default=None, description="Keyset cursor from a previous page."),
    category: str | None = Query(default=None, description="Filter by category."),
    search: str | None = Query(default=None, description="Case-insensitive name search."),
    service: ProductService = Depends(get_product_service),
) -> ProductListResponse:
    """
    Browse the product catalog with keyset pagination.

    Results are ordered by ``updated_at DESC, id DESC``. Pass ``next_cursor``
    from a previous response to fetch the following page.
    """
    try:
        return service.list_products(
            limit=limit,
            cursor=cursor,
            category=category,
            search=search,
        )
    except InvalidCursorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InvalidCategoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
