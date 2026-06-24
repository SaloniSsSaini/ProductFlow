"""Product Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Shared product fields for create and response payloads."""

    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(..., gt=0, decimal_places=2)


class ProductCreate(ProductBase):
    """Payload for creating a single product."""

    pass


class ProductResponse(ProductBase):
    """Product returned to API consumers."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Keyset-paginated product list."""

    items: list[ProductResponse]
    next_cursor: str | None = Field(
        default=None,
        description="Opaque cursor for the next page. Pass as the `cursor` query param.",
    )
    has_more: bool = Field(description="True when additional pages exist.")
