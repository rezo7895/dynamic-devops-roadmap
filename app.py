"""
This Program contains print the current application version through flask
and exit the program.
"""
import os
from flask import Flask, jsonify

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
    app_version = os.getenv("APP_VERSION", VERSION)
    return jsonify({"version": app_version})


if __name__ == "__main__":
    # Run the Flask application
    app.run(host="0.0.0.0", port=5000)