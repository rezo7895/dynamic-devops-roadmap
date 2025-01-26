"""
This Program contains print the current application version and average
temperature accross SenseBoxIDs through flask and exit the program.
"""
from datetime import timezone, timedelta
import datetime
import os
import time
import json
import requests
import valkey
from minio import Minio
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware


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

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)
CACHE_HIT_COUNT = Counter(
    'cache_hit_count',
    'Number of times data was fetched from cache',
    ['sensebox_id']
)
CACHE_MISS_COUNT = Counter(
    'cache_miss_count',
    'Number of times data was fetched from the API',
    ['sensebox_id']
)
UPLOAD_COUNT = Counter(
    'upload_count',
    'Number of successful data uploads to MinIO',
    ['status']  # 'success' or 'failure'
)
TEMPERATURE_STATUS_COUNT = Counter(
    'temperature_status_count',
    'Count of temperature status categories',
    ['status']  # 'Too Cold', 'Good', 'Too Hot'
)


@app.route("/version", methods=["GET"])
def version_endpoint():
    """
    Endpoint to return the application version.
    """
    # Use the environment variable for version or fallback to default
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()
    REQUEST_LATENCY.labels("GET", "/").observe(time.time() - start_time)
    return jsonify({"version": VERSION})


r = valkey.Valkey(host='valkey', port=6379)
last_upload = 0


@app.route("/temperature", methods=["GET"])
def temperature_endpoint():
    """
    Endpoint to return the average temperature based on all sensebox Data
    """
    current_time = time.time()
    global last_upload
    client = Minio(
        "minio:9000",
        access_key="miniouser",
        secret_key="P@ssw0rd",
        secure=False
    )
    bucket_name = 'hivebox'
    destination_file = "temperature_response.txt"
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()
    REQUEST_LATENCY.labels("GET", "/").observe(time.time() - start_time)
    from_date = current_timezone_utc()
    base_url = "https://api.opensensemap.org/boxes/data"
    temperature = {}
    avg_temp = []
    sensebox_ids = os.getenv(
        "SENSEBOX_IDS",
        (
            "5c21ff8f919bf8001adf2488, "
            "5eb99cacd46fb8001b2ce04c, "
            "5e60cf5557703e001bdae7f8"
        )
        ).split(",")
    for i in sensebox_ids:
        cached_data = r.get(f"temperature:{i}")
        if cached_data:
            CACHE_HIT_COUNT.labels(sensebox_id=i).inc()
            temperature[i] = json.loads(cached_data)
        else:
            CACHE_MISS_COUNT.labels(sensebox_id=i).inc()
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
                r.set(f"temperature:{i}", json.dumps(data), ex=300)
            except requests.RequestException as e:
                return jsonify({"error": "Failed to fetch data",
                                "details": str(e)}), 500
    for i, j in temperature.items():
        avg_temp.append(float(j[0]["value"]))
    avg = sum(avg_temp) / len(avg_temp)
    if avg <= 10:
        status = "Too Cold"
    elif 10 <= avg <= 36:
        status = "Good"
    else:
        status = "Too Hot"
    result = {
        "Average_Temperature": f"{avg:.3f}",
        "Status": status
    }
    if current_time - last_upload >= 300:
        try:
            with open(destination_file, "w") as f:
                json.dump(result, f)
            client.fput_object(bucket_name, destination_file, destination_file)
            os.remove(destination_file)
            UPLOAD_COUNT.labels(status="success").inc()
            last_upload = current_time
        except Exception as e:
            print(f"Error uploading data to MinIO: {e}")
            UPLOAD_COUNT.labels(status="failure").inc()
    return jsonify(result)


@app.route("/store", methods=["GET"])
def store_endpoint():
    """
    Endpoint to call temperature endpoint and store the result in MinIO direct
    """
    result = temperature_endpoint().get_json()
    client = Minio(
        "minio:9000",
        access_key="miniouser",
        secret_key="P@ssw0rd",
        secure=False
    )
    bucket_name = 'hivebox'
    destination_file = "temperature_response.txt"
    try:
        with open(destination_file, "w") as f:
            json.dump(result, f)
        client.fput_object(bucket_name, destination_file, destination_file)
        os.remove(destination_file)
        UPLOAD_COUNT.labels(status="success").inc()
    except Exception as e:
        print(f"Error uploading data to MinIO: {e}")
        UPLOAD_COUNT.labels(status="failure").inc()
    return jsonify(result)


if __name__ == "__main__":
    # Run the Flask application
    print(time.time())
    app.run(host="0.0.0.0", port=5000)
