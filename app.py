"""
This Program provides endpoints to fetch the application version 
and current average temperature using Flask.
"""
import os
import requests
from flask import Flask, jsonify

# Application version
VERSION = "v0.0.2"

# Flask app initialization
app = Flask(__name__)

# OpenSenseMap API base URL
OPENSENSEMAP_API_URL = "https://api.opensensemap.org/boxes"

@app.route("/version", methods=["GET"])
def version_endpoint():
    """
    Endpoint to return the application version.
    """
    # Use the environment variable for version or fallback to default
    app_version = os.getenv("APP_VERSION", VERSION)
    return jsonify({"version": app_version})


@app.route("/temperature", methods=["GET"])
def temperature_endpoint():
    """
    Endpoint to return the current average temperature based on senseBox data.
    Data must be no older than 1 hour.
    """
    try:
        # Fetch data from openSenseMap API
        response = requests.get(OPENSENSEMAP_API_URL)
        response.raise_for_status()
        boxes = response.json()

        # Filter temperature data within the last hour
        temperatures = []
        for box in boxes:
            for sensor in box.get("sensors", []):
                if "temperature" in sensor.get("title", "").lower():
                    last_measurement = sensor.get("lastMeasurement")
                    if last_measurement:
                        # Extract the value and check its age
                        value = float(last_measurement.get("value", 0))
                        timestamp = last_measurement.get("createdAt")
                        if is_recent(timestamp):
                            temperatures.append(value)

        # Calculate the average temperature
        if temperatures:
            avg_temperature = sum(temperatures) / len(temperatures)
            return jsonify({"average_temperature": avg_temperature})
        else:
            return jsonify({"error": "No recent temperature data found"}), 404

    except requests.RequestException as e:
        return jsonify({"error": "Failed to fetch data", "details": str(e)}), 500


def is_recent(timestamp):
    """
    Helper function to check if a timestamp is within the last hour.
    """
    from datetime import datetime, timedelta

    try:
        timestamp_dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        return timestamp_dt >= one_hour_ago
    except ValueError:
        return False


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000)