import unittest
from unittest.mock import patch
import app as flask_app  # Import the Flask app from the code above
import requests


class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        """
        Set up the test client for Flask.
        """
        flask_app.app.testing = True
        self.client = flask_app.app.test_client()

    def test_version_endpoint(self):
        """
        Test the /version endpoint.
        """
        response = self.client.get('/version')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"version": flask_app.VERSION})

    @patch("app.requests.get")
    @patch("app.current_timezone_utc")
    def test_temperature_endpoint(self, mock_current_timezone, 
                                  mock_requests_get):
        """
        Test the /temperature endpoint with mocked data.
        """
        # Mock the current_timezone_utc function to return a fixed timestamp
        mock_current_timezone.return_value = "2024-11-23T12:00:00.000Z"

        # Mock the API responses for the SenseBox IDs
        mock_response_data = [
            [{"value": "22.5"}],  # First SenseBox
            [{"value": "23.0"}],  # Second SenseBox
            [{"value": "21.5"}],  # Third SenseBox
        ]
        mock_requests_get.side_effect = [
            unittest.mock.Mock(status_code=200, 
                               json=lambda: mock_response_data[0]),
            unittest.mock.Mock(status_code=200, 
                               json=lambda: mock_response_data[1]),
            unittest.mock.Mock(status_code=200, 
                               json=lambda: mock_response_data[2]),
        ]

        response = self.client.get('/temperature')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"Average_Temperature": "22.333"})

    @patch("app.requests.get")
    def test_temperature_endpoint_api_failure(self, mock_requests_get):
        """
        Test the /temperature endpoint when an API call fails.
        """
        # Mock a failure in the API call
        mock_requests_get.side_effect = requests.RequestException(
            "API failure")

        response = self.client.get('/temperature')
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to fetch data")


if __name__ == "__main__":
    unittest.main()
