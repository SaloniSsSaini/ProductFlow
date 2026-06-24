"""Categories API tests."""

from fastapi.testclient import TestClient

from app.core.categories import get_categories

CATEGORIES_URL = "/api/v1/categories"


def test_list_categories_returns_200(client: TestClient) -> None:
    response = client.get(CATEGORIES_URL)

    assert response.status_code == 200
    body = response.json()
    assert "categories" in body
    assert isinstance(body["categories"], list)
    assert len(body["categories"]) > 0


def test_list_categories_matches_configuration(client: TestClient) -> None:
    response = client.get(CATEGORIES_URL)

    assert response.json()["categories"] == list(get_categories())


def test_list_categories_includes_known_values(client: TestClient) -> None:
    response = client.get(CATEGORIES_URL)
    categories = response.json()["categories"]

    assert "Electronics" in categories
    assert "Books" in categories
