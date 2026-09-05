import pytest
from app import app, get_status


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200

    data = response.get_json()
    assert "version" in data
    assert data["version"] == "v0.2.0"


def test_temperature_endpoint_returns_valid_response(client):
    response = client.get("/temperature")

    assert response.status_code in (200, 503)

    data = response.get_json()

    if response.status_code == 200:
        assert "temperature" in data
        assert "unit" in data
        assert "status" in data
        assert data["unit"] == "celsius"
        assert isinstance(data["temperature"], (int, float))
    else:
        assert "error" in data


def test_get_status_too_cold():
    assert get_status(5) == "Too Cold"


def test_get_status_good():
    assert get_status(20) == "Good"


def test_get_status_too_hot():
    assert get_status(40) == "Too Hot"


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
