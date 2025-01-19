'''Integration Test For all endpoints'''
import json
from unittest.mock import patch, mock_open
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


def test_temperature_endpoint_in_case_no_caching(client):
    """
    Test the Temperature endpoint without redis caching.
    """
    redis_connection = 'app.r'
    connection = 'requests.get'
    minio_client = 'app.Minio'
    open_function = 'builtins.open'
    os_remove = 'os.remove'
    with patch(connection) as mock_get, patch(redis_connection) as mock_r, \
        patch(minio_client) as mock_minio, \
        patch(open_function, mock_open()) as mock_file, \
            patch(os_remove) as mock_os_remove:
        mock_get.return_value.json.return_value = [{"value": 20.0}]
        mock_r.get.return_value = None
        response = client.get('/temperature')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Average_Temperature" in data
        assert "Status" in data
        assert float(data["Average_Temperature"]) == 20
        assert data["Status"] == "Good"
        mock_file.assert_called_once_with("temperature_response.txt", "w")
        mock_file().write.assert_called()
        mock_minio.assert_called_once()
        mock_minio.return_value.fput_object.assert_called_once_with(
            "hivebox", "temperature_response.txt", "temperature_response.txt"
        )
        mock_os_remove.assert_called_once_with("temperature_response.txt")


def test_temperature_endpoint_with_redis_caching(client):
    """
    Test the Temperature endpoint with redis caching.
    """
    redis_connection = 'app.r'
    connection = 'requests.get'
    minio_client = 'app.Minio'
    open_function = 'builtins.open'
    os_remove = 'os.remove'
    with patch(connection) as mock_get, patch(redis_connection) as mock_r, \
        patch(minio_client) as mock_minio, \
        patch(open_function, mock_open()) as mock_file, \
            patch(os_remove) as mock_os_remove:
        mock_get.return_value.json.return_value = [{
            "value": 20.0
        }]
        mock_r.get.return_value = '[{"value": 20.0}]'
        response = client.get('/temperature')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Average_Temperature" in data
        assert "Status" in data
        assert float(data["Average_Temperature"]) == 20
        assert data["Status"] == "Good"
        mock_file.assert_called_once_with("temperature_response.txt", "w")
        mock_file().write.assert_called()
        mock_minio.assert_called_once()
        mock_minio.return_value.fput_object.assert_called_once_with(
            "hivebox", "temperature_response.txt", "temperature_response.txt"
        )
        mock_os_remove.assert_called_once_with("temperature_response.txt")


def test_temperature_endpoint_failure(client):
    """
    Test the temperature endpoint for a failure scenario.
    """
    redis_connection = 'app.r'
    connection = 'requests.get'
    with patch(connection) as mock_get, patch(redis_connection) as mock_r:
        mock_get.side_effect = requests.exceptions.RequestException(
                        "Network Error")
        mock_r.get.return_value = None
        response = client.get('/temperature')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert data["error"] == "Failed to fetch data"
