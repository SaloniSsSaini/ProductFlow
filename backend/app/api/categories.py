"""Product category API routes."""

from fastapi import APIRouter

from app.core.categories import get_categories
from app.schemas.categories import CategoriesResponse

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoriesResponse, summary="List categories")
def list_categories() -> CategoriesResponse:
    """Return the configured category list used for product filtering and validation."""
    return CategoriesResponse(categories=list(get_categories()))
