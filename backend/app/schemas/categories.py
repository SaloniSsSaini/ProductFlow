"""Category list response schemas."""

from pydantic import BaseModel, Field


class CategoriesResponse(BaseModel):
    """Configured product categories."""

    categories: list[str] = Field(description="Valid category names for filtering and creation.")
