"""Product domain tests."""

from decimal import Decimal

import pytest

from app.core.categories import get_categories
from app.schemas.product import ProductCreate
from app.services.product_service import InvalidCategoryError, ProductService


def test_create_product_persists_row(product_service: ProductService) -> None:
    category = get_categories()[0]
    payload = ProductCreate(
        name="Premium Wireless Headphones 1001",
        category=category,
        price=Decimal("149.99"),
    )

    product = product_service.create_product(payload)

    assert product.id is not None
    assert product.name == payload.name
    assert product.category == category
    assert product.price == payload.price
    assert product.created_at is not None
    assert product.updated_at is not None


def test_create_product_rejects_invalid_category(product_service: ProductService) -> None:
    payload = ProductCreate(
        name="Mystery Item",
        category="NotARealCategory",
        price=Decimal("9.99"),
    )

    with pytest.raises(InvalidCategoryError):
        product_service.create_product(payload)


def test_bulk_create_products(product_service: ProductService) -> None:
    category = get_categories()[1]
    batch = [
        ProductCreate(
            name=f"Bulk Product {index}",
            category=category,
            price=Decimal("19.99"),
        )
        for index in range(50)
    ]

    inserted = product_service.bulk_create_products(batch)

    assert inserted == 50


def test_total_products_returns_count(product_service: ProductService) -> None:
    initial_count = product_service.total_products()
    category = get_categories()[2]

    product_service.create_product(
        ProductCreate(
            name="Count Test Product",
            category=category,
            price=Decimal("29.99"),
        )
    )

    assert product_service.total_products() == initial_count + 1
