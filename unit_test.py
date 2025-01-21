'''Unit Test For all endpoints'''
import json
from unittest.mock import mock_open
import requests
import pytest
from app import app, VERSION


@pytest.fixture
def client_fixture():
    '''Simulates a unit test client'''
    with app.test_client() as client:
        yield client


def test_version(client_fixture):
    """
    Test the version endpoint.
    """
    response = client_fixture.get('/version')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'version' in data
    assert data['version'] == VERSION


def test_temperature_success_without_redis_caching(client_fixture, mocker):
    """
    Test the temperature endpoint for a successful response.
    """
    # Mocking the external request to simulate OpenSenseMap API response
    mock_response = [
        {"value": "20.5"},
        {"value": "22.0"},
        {"value": "18.0"}
    ]
    mocker.patch('app.requests.get', return_value=mocker.Mock(
                                status_code=200, json=lambda: mock_response
                                ))
    mock_redis = mocker.patch('app.r')
    mock_minio = mocker.patch('app.Minio')
    mock_file = mocker.patch('builtins.open', mock_open())
    mock_os_remove = mocker.patch('os.remove')

    mock_redis.get.return_value = None
    response = client_fixture.get('/temperature')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'Average_Temperature' in data
    # Update the expected value to match the calculated average
    assert float(data['Average_Temperature']) == pytest.approx(20.5, rel=1e-3)
    mock_file.assert_called_once_with("temperature_response.txt", "w")
    mock_file().write.assert_called()
    mock_minio.assert_called_once()
    mock_minio.return_value.fput_object.assert_called_once_with(
            "hivebox", "temperature_response.txt", "temperature_response.txt"
        )
    mock_os_remove.assert_called_once_with("temperature_response.txt")


def test_temperature_success_with_redis_caching(client_fixture, mocker):
    """
    Test the temperature endpoint for a successful response.
    """
    # Mocking the external request to simulate OpenSenseMap API response
    mock_response = [
        {"value": "20.5"},
        {"value": "22.0"},
        {"value": "18.0"}
    ]
    mocker.patch('app.requests.get', return_value=mocker.Mock(
                                status_code=200, json=lambda: mock_response
                                ))
    mock_redis = mocker.patch('app.r')
    mock_minio = mocker.patch('app.Minio')
    mock_file = mocker.patch('builtins.open', mock_open())
    mock_os_remove = mocker.patch('os.remove')
    mocker.patch('app.time.time', return_value=300)
    mocker.patch('app.last_upload', 0)
    mock_redis.get.return_value = '[{"value": 20.5}]'
    response = client_fixture.get('/temperature')
    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'Average_Temperature' in data
    # Update the expected value to match the calculated average
    assert float(data['Average_Temperature']) == pytest.approx(20.5, rel=1e-3)
    mock_file.assert_called_once_with("temperature_response.txt", "w")
    mock_file().write.assert_called()
    mock_minio.assert_called_once()
    mock_minio.return_value.fput_object.assert_called_once_with(
            "hivebox", "temperature_response.txt", "temperature_response.txt"
        )
    mock_os_remove.assert_called_once_with("temperature_response.txt")


def test_temperature_failure(client_fixture, mocker):
    """
    Test the temperature endpoint for a failure scenario.
    """
    # Mocking the external request to simulate a failure (timeout)
    mocker.patch('app.requests.get',
                 side_effect=requests.exceptions.RequestException(
                     "Request failed"
                     ))
    mock_redis = mocker.patch('app.r')
    mock_redis.get.return_value = None
    response = client_fixture.get('/temperature')
    data = json.loads(response.data)
    assert response.status_code == 500
    assert 'error' in data
    assert data['error'] == 'Failed to fetch data'


def test_temperature_status(client_fixture, mocker):
    """
    Test the temperature status based on various temperature values.
    """
    mock_response = [
        {"value": "15.0"},
        {"value": "16.0"},
        {"value": "17.0"}
    ]
    # Mocking the external request with specific temperature values
    mocker.patch('app.requests.get', return_value=mocker.Mock(
                                    status_code=200,
                                    json=lambda: mock_response))
    mock_redis = mocker.patch('app.r')
    mock_minio = mocker.patch('app.Minio')
    mock_file = mocker.patch('builtins.open', mock_open())
    mock_os_remove = mocker.patch('os.remove')
    mock_redis.get.return_value = None
    mocker.patch('app.time.time', return_value=300)
    mocker.patch('app.last_upload', 0)
    response = client_fixture.get('/temperature')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data['Status'] == 'Good'
    mock_file.assert_called_once_with("temperature_response.txt", "w")
    mock_file().write.assert_called()
    mock_minio.assert_called_once()
    mock_minio.return_value.fput_object.assert_called_once_with(
        "hivebox", "temperature_response.txt", "temperature_response.txt"
        )
    mock_os_remove.assert_called_once_with("temperature_response.txt")
