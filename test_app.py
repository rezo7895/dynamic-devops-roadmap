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
    assert data["version"] == "v0.0.2"


def test_temperature_endpoint(client, mocker):
    mock_data = [
        {
            "sensors": [
                {
                    "title": "Temperature",
                    "lastMeasurement": {
                        "value": "22.5",
                        "createdAt": "2024-11-20T12:00:00Z",
                    },
                }
            ]
        }
    ]
    mocker.patch("requests.get", return_value=mocker.Mock(json=lambda: mock_data))
    response = client.get("/temperature")
    assert response.status_code == 200
    data = response.get_json()
    assert "average_temperature" in data