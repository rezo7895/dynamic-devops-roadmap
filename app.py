"""
This Program contains print the current application version and average
temperature accross SenseBoxIDs through flask and exit the program.
"""
from datetime import timezone, timedelta
import datetime
import requests
from flask import Flask, jsonify


def current_timezone_utc():
    '''
    Function get date 1 hour earlier of current timestamp in utc timezone
    '''
    dt = datetime.datetime.now(timezone.utc)
    dt = dt - timedelta(hours=1)
    formatted_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return formatted_timestamp
# Application version


VERSION = "v0.0.2"
# Flask app initialization
app = Flask(__name__)


@app.route("/version", methods=["GET"])
def version_endpoint():
    """
    Endpoint to return the application version.
    """
    # Use the environment variable for version or fallback to default
    return jsonify({"version": VERSION})


@app.route("/temperature", methods=["GET"])
def temperature_edpoint():
    """
    Endpoint to return the average temperature based on all sensebox Data
    """
    from_date = current_timezone_utc()
    base_url = "https://api.opensensemap.org/boxes/data"
    temperature = {}
    avg_temp = []
    sensebox_ids = ["5c21ff8f919bf8001adf2488",
                    "5eb99cacd46fb8001b2ce04c",
                    "5e60cf5557703e001bdae7f8"]
    for i in sensebox_ids:
        params = {
            "boxId": i,
            "phenomenon": "Temperatur",
            "from-date": from_date,
            "format": "json"
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            temperature[i] = data
        except requests.RequestException as e:
            return jsonify({"error": "Failed to fetch data",
                            "details": str(e)}), 500
    for i, j in temperature.items():
        avg_temp.append(float(j[0]["value"]))
    avg = sum(avg_temp)/len(avg_temp)
    if avg <= 10:
        status = "Too Cold"
    elif 10 <= avg <= 36:
        status = "Good"
    else:
        status = "Too Hot"
    return jsonify({
        "Average_Temperature":  f"{avg:.3f}",
        "Status": status
        })


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000)
