"""Product listing API tests."""

import pytest

PRODUCTS_API = "/api/v1/products"


def test_list_products_first_page(api_client, catalog_products) -> None:
    response = api_client.get(PRODUCTS_API, params={"limit": 10})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["has_more"] is True
    assert body["next_cursor"] is not None

    timestamps = [item["updated_at"] for item in body["items"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_list_products_second_page(api_client, catalog_products) -> None:
    first = api_client.get(PRODUCTS_API, params={"limit": 10}).json()
    second = api_client.get(
        PRODUCTS_API,
        params={"limit": 10, "cursor": first["next_cursor"]},
    )

    assert second.status_code == 200
    body = second.json()
    assert len(body["items"]) == 10
    assert body["has_more"] is True


def test_list_products_no_duplicate_ids_between_pages(api_client, catalog_products) -> None:
    first = api_client.get(PRODUCTS_API, params={"limit": 10}).json()
    second = api_client.get(
        PRODUCTS_API,
        params={"limit": 10, "cursor": first["next_cursor"]},
    ).json()

    first_ids = {item["id"] for item in first["items"]}
    second_ids = {item["id"] for item in second["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_list_products_category_filter(api_client, catalog_products) -> None:
    category = catalog_products[0].category
    expected = sum(1 for product in catalog_products if product.category == category)

    response = api_client.get(PRODUCTS_API, params={"category": category, "limit": 100})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == expected
    assert all(item["category"] == category for item in body["items"])


def test_list_products_search(api_client, catalog_products) -> None:
    response = api_client.get(PRODUCTS_API, params={"search": "Alpha", "limit": 100})

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) > 0
    assert all("Alpha" in item["name"] for item in body["items"])


def test_list_products_invalid_cursor(api_client, catalog_products) -> None:
    response = api_client.get(PRODUCTS_API, params={"cursor": "not-a-valid-cursor"})

    assert response.status_code == 400
    assert "cursor" in response.json()["detail"].lower()


def test_list_products_invalid_category(api_client, catalog_products) -> None:
    response = api_client.get(PRODUCTS_API, params={"category": "NotARealCategory"})

    assert response.status_code == 400


@pytest.mark.parametrize("limit", [1, 10, 20])
def test_list_products_respects_limit(api_client, catalog_products, limit: int) -> None:
    response = api_client.get(PRODUCTS_API, params={"limit": limit})

    assert response.status_code == 200
    assert len(response.json()["items"]) == limit
