'''Integration Test For all endpoints'''
import json
from unittest.mock import patch
import requests
import pytest
from app import app, VERSION


@pytest.fixture
def client():
    '''Simulates an integration test client'''
    with app.test_client() as client:
        yield client


def test_version_endpoint(client):
    """
    Test the version endpoint.
    """
    response = client.get('/version')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "version" in data
    assert data["version"] == VERSION


def test_temperature_endpoint(client):
    """
    Test the Temperature endpoint.
    """
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = [{
            "value": 20.0
        }]
        response = client.get('/temperature')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Average_Temperature" in data
        assert "Status" in data
        assert float(data["Average_Temperature"]) == 20
        assert data["Status"] == "Good"


def test_temperature_endpoint_failure(client):
    """
    Test the temperature endpoint for a failure scenario.
    """
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException(
                        "Network Error")
        response = client.get('/temperature')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Failed to fetch data"
