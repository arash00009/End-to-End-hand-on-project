import pytest
from app import app

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
    assert data["version"] == "v0.1.0"

def test_temperature_endpoint_returns_valid_response(client):
    response = client.get("/temperature")

    # Endpointen ska antingen lyckas (200) eller tydligt säga att data saknas (503)
    assert response.status_code in (200, 503)

    data = response.get_json()

    if response.status_code == 200:
        assert "temperature" in data
        assert "unit" in data
        assert data["unit"] == "celsius"
        assert isinstance(data["temperature"], (int, float))
    else:
        assert "error" in data
