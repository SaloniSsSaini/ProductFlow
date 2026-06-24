"""Health endpoint tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient

HEALTH_URL = "/api/v1/health"


def test_root_returns_service_info(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "ProductFlow"
    assert "health" in body


def test_health_returns_200_when_database_connected(client: TestClient) -> None:
    with patch("app.api.health.check_database_connection", return_value=True):
        response = client.get(HEALTH_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "ProductFlow"
    assert body["status"] == "ok"
    assert body["database"] == "connected"
    assert "timestamp" in body


def test_health_returns_503_when_database_disconnected(client: TestClient) -> None:
    with patch("app.api.health.check_database_connection", return_value=False):
        response = client.get(HEALTH_URL)

    assert response.status_code == 503
    body = response.json()
    assert body["service"] == "ProductFlow"
    assert body["status"] == "degraded"
    assert body["database"] == "disconnected"
    assert "timestamp" in body


def test_health_response_body_shape_is_identical_regardless_of_status(
    client: TestClient,
) -> None:
    """503 responses keep the same JSON schema as 200 responses."""
    with patch("app.api.health.check_database_connection", return_value=True):
        ok_body = client.get(HEALTH_URL).json()
    with patch("app.api.health.check_database_connection", return_value=False):
        degraded_body = client.get(HEALTH_URL).json()

    assert set(ok_body.keys()) == set(degraded_body.keys())
    assert set(ok_body.keys()) == {
        "status",
        "service",
        "environment",
        "database",
        "timestamp",
    }
