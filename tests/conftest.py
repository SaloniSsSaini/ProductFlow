"""Pytest configuration and shared fixtures."""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.categories import get_categories
from app.core.config import get_settings
from app.database.session import SessionLocal, check_database_connection, engine, get_db
from app.main import create_app
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.product_service import ProductService

PRODUCTS_API = "/api/v1/products"


@pytest.fixture(scope="session")
def app():
    """Create a fresh application instance for the test session."""
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """HTTP client for integration tests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def postgres_available() -> bool:
    """True when PostgreSQL accepts connections."""
    return check_database_connection()


@pytest.fixture(scope="session")
def products_schema_ready(postgres_available) -> bool:
    """True when the products table exists (migrations applied)."""
    if not postgres_available:
        return False
    inspector = inspect(engine)
    return "products" in inspector.get_table_names()


@pytest.fixture
def db_session(postgres_available, products_schema_ready) -> Session:
    """Yield a database session that rolls back after each test."""
    if not postgres_available:
        pytest.skip("PostgreSQL is not available")
    if not products_schema_ready:
        pytest.skip("products table missing — run: cd backend && alembic upgrade head")

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def api_client(app, db_session: Session):
    """HTTP client with DB session override for isolated API tests."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def catalog_products(db_session: Session) -> list[Product]:
    """Insert products with distinct updated_at values for pagination tests."""
    base_time = datetime.now(UTC)
    categories = list(get_categories())
    products: list[Product] = []

    for index in range(40):
        products.append(
            Product(
                id=uuid.uuid4(),
                name=f"Alpha Widget {index}" if index % 2 == 0 else f"Beta Gadget {index}",
                category=categories[index % len(categories)],
                price=Decimal("10.00") + Decimal(index),
                created_at=base_time - timedelta(minutes=index),
                updated_at=base_time - timedelta(minutes=index),
            )
        )

    db_session.add_all(products)
    db_session.flush()
    return products


@pytest.fixture
def product_repository(db_session: Session) -> ProductRepository:
    """Product repository bound to the test session."""
    return ProductRepository(db_session)


@pytest.fixture
def product_service(product_repository: ProductRepository) -> ProductService:
    """Product service bound to the test repository."""
    return ProductService(product_repository)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Ensure settings are reloaded between tests when env vars change."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
