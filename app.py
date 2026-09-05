from flask import Flask, jsonify
import requests
from datetime import datetime, timezone

app = Flask(__name__)

__version__ = "v0.1.0"

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": __version__})

@app.route("/temperature", methods=["GET"])
def temperature():
    readings = []

    for box_id in SENSEBOX_IDS:
        url = f"https://api.opensensemap.org/boxes/{box_id}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            continue

        data = response.json()

        for sensor in data.get("sensors", []):
            if sensor.get("title", "").lower() == "temperatur" or sensor.get("title", "").lower() == "temperature":
                last = sensor.get("lastMeasurement")
                if last and last.get("value"):
                    readings.append(float(last["value"]))

    if not readings:
        return jsonify({"error": "No temperature data available"}), 503

    average = sum(readings) / len(readings)

    return jsonify({
        "temperature": round(average, 2),
        "unit": "celsius",
        "sensors_used": len(readings)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
